"""Use case: edit the general data of a draft tournament."""

from collections.abc import Callable
from datetime import datetime

from server.core.entities.tournament import Tournament
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.create_tournament import CreateTournamentInput
from server.core.use_cases.get_tournament import GetTournament
from server.core.use_cases.tournament_name_availability import (
    ensure_name_available,
)


class UpdateTournament:
    def __init__(
        self, repository: TournamentRepository, clock: Callable[[], datetime],
    ) -> None:
        self._repository = repository
        self._get = GetTournament(repository)
        self._clock = clock

    def execute(self, tournament_id: str, data: CreateTournamentInput) -> Tournament:
        tournament = self._get.execute(tournament_id).edit(
            name=data.name, tournament_format=data.tournament_format,
            modality=data.modality, start_date=data.start_date,
            end_date=data.end_date, updated_at=self._clock(),
        )
        ensure_name_available(self._repository, data.name, tournament_id)
        self._repository.update(tournament)
        return tournament
