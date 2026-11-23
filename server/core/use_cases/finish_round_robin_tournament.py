"""Finish a round-robin tournament after every match is completed."""

from collections.abc import Callable
from datetime import datetime

from server.core.entities.match import MatchStatus
from server.core.entities.tournament import Tournament
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


class FinishRoundRobinTournament:
    def __init__(
        self,
        tournament_repository: TournamentRepository,
        matches: MatchRepository,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._get = GetTournament(tournament_repository)
        self._matches = matches
        self._clock = clock or datetime.now
        self._repository = tournament_repository

    def execute(self, tournament_id: str) -> Tournament:
        tournament = self._get.execute(tournament_id)
        pending = [
            match
            for match in self._matches.list_for_tournament(tournament_id)
            if match.status is not MatchStatus.COMPLETED
        ]
        if pending:
            raise InvalidTournamentError(
                "Não é possível encerrar: existem partidas pendentes."
            )
        finished = tournament.finish_round_robin(self._clock())
        self._repository.update(finished)
        return finished
