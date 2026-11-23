"""Use case: list the persisted tournaments."""

from server.core.entities.tournament import Tournament
from server.core.interfaces.tournament_repository import TournamentRepository


class ListTournaments:
    """Lists every tournament, most recently created first."""

    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Tournament]:
        return sorted(
            self._repository.list_all(),
            key=lambda tournament: tournament.created_at,
            reverse=True,
        )
