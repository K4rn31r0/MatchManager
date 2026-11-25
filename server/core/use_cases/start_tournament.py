"""Start a tournament using the starter of its format."""

from collections.abc import Mapping
from typing import Protocol

from server.core.entities.tournament import Tournament, TournamentFormat
from server.core.errors import InvalidTournamentError
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


class TournamentStarter(Protocol):
    """Format-specific strategy that validates and starts a tournament."""

    def execute(self, tournament_id: str) -> Tournament:
        """Start the tournament or raise a domain error explaining why not."""


class StartTournament:
    """Starts any tournament by delegating to the strategy of its format.

    New formats are supported by registering another starter, without
    changing this workflow.
    """

    def __init__(
        self,
        tournaments: TournamentRepository,
        starters: Mapping[TournamentFormat, TournamentStarter],
    ) -> None:
        self._get_tournament = GetTournament(tournaments)
        self._starters = dict(starters)

    def execute(self, tournament_id: str) -> Tournament:
        tournament = self._get_tournament.execute(tournament_id)
        starter = self._starters.get(tournament.tournament_format)
        if starter is None:
            raise InvalidTournamentError(
                "Este formato de torneio não pode ser iniciado."
            )
        return starter.execute(tournament_id)
