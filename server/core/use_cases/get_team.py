"""Use case: look up a single team."""

from server.core.entities.team import Team
from server.core.errors import TeamNotFoundError
from server.core.interfaces.team_repository import TeamRepository


def require_team(repository: TeamRepository, team_id: str) -> Team:
    """Return the team, raising TeamNotFoundError when it does not exist."""
    team = repository.get(team_id)
    if team is None:
        raise TeamNotFoundError("Equipe não encontrada.")
    return team


class GetTeam:
    """Returns one team by its id."""

    def __init__(self, repository: TeamRepository) -> None:
        self._repository = repository

    def execute(self, team_id: str) -> Team:
        """Return the team.

        Raises:
            TeamNotFoundError: no team has the given id.
        """
        return require_team(self._repository, team_id)
