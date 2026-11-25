"""Register a result for a round-robin match."""

from dataclasses import dataclass

from server.core.entities.match import Match, MatchResult
from server.core.entities.tournament import TournamentFormat
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class RoundRobinResultInput:
    result: MatchResult | None = None
    first_score: int | None = None
    second_score: int | None = None
    first_team_stats: dict[str, int] | None = None
    second_team_stats: dict[str, int] | None = None


class RecordRoundRobinResult:
    def __init__(
        self,
        tournament_repository: TournamentRepository,
        matches: MatchRepository,
    ) -> None:
        self._get = GetTournament(tournament_repository)
        self._matches = matches

    def execute(
        self,
        tournament_id: str,
        match_id: str,
        data: RoundRobinResultInput,
    ) -> Match:
        tournament = self._get.execute(tournament_id)
        if tournament.tournament_format is not TournamentFormat.ROUND_ROBIN:
            raise InvalidTournamentError(
                "Esta operação só pode ser usada em pontos corridos."
            )
        tournament.ensure_accepts_results()
        match = self._matches.get(match_id)
        if match is None or match.tournament_id != tournament_id:
            raise InvalidTournamentError("Partida não encontrada.")
        if data.result is None:
            raise InvalidTournamentError("Informe vitória, empate ou derrota.")
        try:
            recorded = match.record_result(
                result=data.result,
                first_score=data.first_score,
                second_score=data.second_score,
                first_team_stats=data.first_team_stats,
                second_team_stats=data.second_team_stats,
            )
        except ValueError as error:
            if str(error) == "placar completo":
                message = "Informe o placar completo ou não informe placar."
            else:
                message = "O placar não corresponde ao resultado informado."
            raise InvalidTournamentError(message) from None
        self._matches.update(recorded)
        return recorded
