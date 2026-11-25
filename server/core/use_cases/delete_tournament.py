"""Use case: remove a tournament after explicit confirmation."""

from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.registration_repository import (
    RegistrationRepository,
)
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


class DeleteTournament:
    """Deletes a tournament together with its registrations and matches.

    Registrations and matches have no meaning without their tournament, so
    they are removed as well and no orphan data is left behind.
    """

    def __init__(
        self,
        repository: TournamentRepository,
        registrations: RegistrationRepository,
        matches: MatchRepository,
    ) -> None:
        self._repository = repository
        self._registrations = registrations
        self._matches = matches
        self._get = GetTournament(repository)

    def execute(self, tournament_id: str, *, confirmed: bool) -> None:
        """Delete the tournament and everything that belongs to it.

        Raises:
            TournamentNotFoundError: no tournament has the given id.
            InvalidTournamentError: the deletion was not confirmed.
        """
        self._get.execute(tournament_id)
        if not confirmed:
            raise InvalidTournamentError("Confirme a exclusão do torneio.")
        self._matches.delete_for_tournament(tournament_id)
        self._registrations.remove_all_for_tournament(tournament_id)
        self._repository.delete(tournament_id)
