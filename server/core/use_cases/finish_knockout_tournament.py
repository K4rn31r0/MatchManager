"""Finish a knockout tournament after every bracket match is complete."""

from collections.abc import Callable
from datetime import datetime

from server.core.entities.knockout_bracket import bracket_size, knockout_round_count
from server.core.entities.match import MatchResult, MatchStatus
from server.core.entities.tournament import (
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


class FinishKnockoutTournament:
    def __init__(
        self,
        tournament_repository: TournamentRepository,
        matches: MatchRepository,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._get_tournament = GetTournament(tournament_repository)
        self._tournaments = tournament_repository
        self._matches = matches
        self._clock = clock or datetime.now

    def execute(self, tournament_id: str) -> Tournament:
        tournament = self._get_tournament.execute(tournament_id)
        if tournament.tournament_format is not TournamentFormat.KNOCKOUT:
            raise InvalidTournamentError(
                "O encerramento solicitado não corresponde ao formato "
                "do torneio."
            )
        if tournament.status is not TournamentStatus.IN_PROGRESS:
            raise InvalidTournamentError(
                "Só é possível encerrar torneios em andamento."
            )
        config = tournament.knockout
        if config is None or len(config.initial_order) < 2:
            raise InvalidTournamentError("Gere um chaveamento válido.")

        matches = self._matches.list_for_tournament(tournament_id)
        if any(
            match.status is not MatchStatus.COMPLETED
            or match.result not in (
                MatchResult.FIRST_WIN,
                MatchResult.SECOND_WIN,
            )
            for match in matches
        ):
            raise InvalidTournamentError(
                "Não é possível encerrar: existem partidas pendentes "
                "ou sem vencedor."
            )

        final_round = knockout_round_count(len(config.initial_order))
        final_matches = [
            match for match in matches
            if match.round_number == final_round
        ]
        if (
            final_round == 0
            or len(final_matches) != 1
            or final_matches[0].first_team_id is None
            or final_matches[0].second_team_id is None
        ):
            raise InvalidTournamentError(
                "Não é possível encerrar: a partida final não foi concluída."
            )

        finished = tournament.finish_knockout(self._clock())
        self._tournaments.update(finished)
        return finished
