"""Use case: create a tournament in the draft status."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

from server.core.entities.tournament import Tournament, TournamentFormat
from server.core.use_cases.tournament_name_availability import (
    ensure_name_available,
)
from server.core.interfaces.tournament_repository import TournamentRepository


@dataclass(frozen=True, kw_only=True)
class CreateTournamentInput:
    """Data provided by the user to create a tournament."""

    name: str
    tournament_format: TournamentFormat
    modality: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class CreateTournament:
    """Creates a draft tournament with a unique name."""

    def __init__(
        self,
        repository: TournamentRepository,
        id_generator: Callable[[], str],
        clock: Callable[[], datetime],
    ) -> None:
        self._repository = repository
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, data: CreateTournamentInput) -> Tournament:
        """Create and persist the tournament.

        Raises:
            InvalidTournamentError: the data breaks a tournament invariant.
            DuplicateTournamentNameError: the name is already in use.
        """
        ensure_name_available(self._repository, data.name)
        tournament = Tournament.create_draft(
            id=self._id_generator(),
            name=data.name,
            tournament_format=data.tournament_format,
            created_at=self._clock(),
            modality=data.modality,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        self._repository.add(tournament)
        return tournament
