"""Use case: consult a tournament."""

from server.core.entities.tournament import Tournament
from server.core.errors import TournamentNotFoundError
from server.core.interfaces.tournament_repository import TournamentRepository


class GetTournament:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(self, tournament_id: str) -> Tournament:
        tournament = self._repository.get(tournament_id)
        if tournament is None:
            raise TournamentNotFoundError("Torneio não encontrado.")
        return tournament
