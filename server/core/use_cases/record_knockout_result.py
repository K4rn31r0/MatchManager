"""Record a winner and advance it through a knockout bracket."""

from dataclasses import dataclass, replace

from server.core.entities.knockout_bracket import bracket_size
from server.core.entities.match import Match, MatchResult, MatchStatus
from server.core.entities.tournament import (
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class KnockoutResultInput:
    result: MatchResult | None = None
    first_score: int | None = None
    second_score: int | None = None


class RecordKnockoutResult:
    def __init__(
        self,
        tournament_repository: TournamentRepository,
        matches: MatchRepository,
    ) -> None:
        self._get_tournament = GetTournament(tournament_repository)
        self._matches = matches

    def execute(
        self,
        tournament_id: str,
        match_id: str,
        data: KnockoutResultInput,
    ) -> Match:
        tournament = self._get_tournament.execute(tournament_id)
        if tournament.tournament_format is not TournamentFormat.KNOCKOUT:
            raise InvalidTournamentError(
                "Esta operação só pode ser usada em mata-mata."
            )
        if tournament.status is not TournamentStatus.IN_PROGRESS:
            raise InvalidTournamentError(
                "Só é possível registrar resultados em torneios iniciados."
            )
        match = self._matches.get(match_id)
        if match is None or match.tournament_id != tournament_id:
            raise InvalidTournamentError("Partida não encontrada.")
        if data.result not in (MatchResult.FIRST_WIN, MatchResult.SECOND_WIN):
            raise InvalidTournamentError(
                "Informe o vencedor da partida."
            )
        tournament_matches = self._matches.list_for_tournament(tournament_id)
        if any(
            item.round_number > match.round_number
            and item.status is MatchStatus.COMPLETED
            for item in tournament_matches
        ):
            raise InvalidTournamentError(
                "Não é possível corrigir o resultado após uma "
                "partida subsequente."
            )
        try:
            recorded = match.record_result(
                result=data.result,
                first_score=data.first_score,
                second_score=data.second_score,
                first_team_stats=None,
                second_team_stats=None,
            )
        except ValueError as error:
            if str(error) == "placar completo":
                message = "Informe o placar completo ou não informe placar."
            elif str(error) == "partida aguardando equipes":
                message = "A partida ainda aguarda equipes."
            else:
                message = "O placar não corresponde ao resultado informado."
            raise InvalidTournamentError(message) from None
        next_match = self._find_next_match(
            tournament,
            match,
            tournament_matches,
        )
        if next_match is not None:
            winner_id = (
                match.first_team_id
                if data.result is MatchResult.FIRST_WIN
                else match.second_team_id
            )
            if winner_id is None:
                raise InvalidTournamentError(
                    "A partida ainda aguarda equipes."
                )
            advanced = self._advance(next_match, match, winner_id)
            self._matches.update(advanced)
        self._matches.update(recorded)
        return recorded

    def _find_next_match(
        self,
        tournament: Tournament,
        match: Match,
        tournament_matches: list[Match],
    ) -> Match | None:
        config = tournament.knockout
        if (
            config is None
            or len(config.initial_order) < 2
            or match.bracket_position is None
        ):
            raise InvalidTournamentError(
                "O chaveamento da partida não é válido."
            )
        round_count = bracket_size(len(config.initial_order)).bit_length() - 1
        if not 1 <= match.round_number <= round_count:
            raise InvalidTournamentError(
                "A fase da partida não é válida no chaveamento."
            )
        if match.round_number == round_count:
            return None
        next_position = (match.bracket_position + 1) // 2
        next_matches = [
            item for item in tournament_matches
            if (
                item.round_number == match.round_number + 1
                and item.bracket_position == next_position
            )
        ]
        if len(next_matches) != 1:
            raise InvalidTournamentError(
                "A partida seguinte não foi encontrada no chaveamento."
            )
        return next_matches[0]

    @staticmethod
    def _advance(
        next_match: Match,
        match: Match,
        winner_id: str,
    ) -> Match:
        if match.bracket_position is None:
            raise InvalidTournamentError(
                "O chaveamento da partida não é válido."
            )
        winner_field = (
            "first_team_id" if match.bracket_position % 2 else "second_team_id"
        )
        if next_match.status is MatchStatus.COMPLETED:
            raise InvalidTournamentError(
                "Não é possível alterar o resultado após uma "
                "partida subsequente."
            )
        return replace(next_match, **{winner_field: winner_id})
