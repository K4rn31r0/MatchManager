"""Use case: remove a tournament after explicit confirmation."""

from server.core.errors import InvalidTournamentError
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


class DeleteTournament:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository
        self._get = GetTournament(repository)

    def execute(self, tournament_id: str, *, confirmed: bool) -> None:
        self._get.execute(tournament_id)
        if not confirmed:
            raise InvalidTournamentError("Confirme a exclusão do torneio.")
        self._repository.delete(tournament_id)
