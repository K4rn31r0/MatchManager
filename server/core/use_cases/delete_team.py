"""Use case: delete a team."""

from server.core.errors import TeamInStartedTournamentError
from server.core.interfaces.registration_repository import (
    RegistrationRepository,
)
from server.core.interfaces.team_participation_query import (
    TeamParticipationQuery,
)
from server.core.interfaces.team_repository import TeamRepository
from server.core.use_cases.get_team import require_team


class DeleteTeam:
    """Deletes a team that does not play any started tournament.

    The team's registrations in draft tournaments are removed as well, so
    no tournament keeps a reference to a team that no longer exists.
    """

    def __init__(
        self,
        repository: TeamRepository,
        participation: TeamParticipationQuery,
        registrations: RegistrationRepository,
    ) -> None:
        self._repository = repository
        self._participation = participation
        self._registrations = registrations

    def execute(self, team_id: str) -> None:
        """Delete the team and its registrations.

        Raises:
            TeamNotFoundError: no team has the given id.
            TeamInStartedTournamentError: the team plays a tournament that
                is in progress or finished.
        """
        team = require_team(self._repository, team_id)
        if self._participation.is_in_started_tournament(team.id):
            raise TeamInStartedTournamentError(
                f"A equipe “{team.name}” participa de um torneio iniciado "
                "e não pode ser excluída."
            )
        self._registrations.remove_all_for_team(team.id)
        self._repository.delete(team.id)
