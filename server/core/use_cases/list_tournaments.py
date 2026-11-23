"""Use case: list the persisted tournaments."""

from server.core.entities.names import normalize_name
from server.core.entities.tournament import Tournament, TournamentStatus
from server.core.interfaces.tournament_repository import TournamentRepository


class ListTournaments:
    """Lists matching tournaments, ordered by recent activity by default."""

    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(
        self, search: str = "", status: TournamentStatus | None = None,
        order: str = "activity",
    ) -> list[Tournament]:
        query = normalize_name(search)
        tournaments = [
            tournament for tournament in self._repository.list_all()
            if (status is None or tournament.status is status)
            and query in normalize_name(tournament.name)
        ]
        if order == "name":
            return sorted(tournaments, key=lambda item: normalize_name(item.name))
        if order == "format":
            return sorted(tournaments, key=lambda item: item.tournament_format.value)
        if order == "status":
            return sorted(tournaments, key=lambda item: item.status.value)
        return sorted(tournaments, key=lambda item: item.last_activity, reverse=True)

    def participant_counts(self) -> dict[str, int]:
        return self._repository.participant_counts()
