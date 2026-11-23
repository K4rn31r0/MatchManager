"""Use case: create a team."""

from collections.abc import Callable

from server.core.entities.team import Team
from server.core.interfaces.team_repository import TeamRepository
from server.core.use_cases.team_data import TeamData
from server.core.use_cases.team_name_availability import (
    ensure_team_name_is_available,
)


class CreateTeam:
    """Creates a team with a unique name."""

    def __init__(
        self,
        repository: TeamRepository,
        id_generator: Callable[[], str],
    ) -> None:
        self._repository = repository
        self._id_generator = id_generator

    def execute(self, data: TeamData) -> Team:
        """Create and persist the team.

        Raises:
            InvalidTeamError: the data breaks a team invariant.
            DuplicateTeamNameError: the name is already in use.
        """
        team = self.prepare(data)
        self._repository.add(team)
        return team

    def prepare(self, data: TeamData) -> Team:
        """Validate and build a new team for a combined persistence operation."""
        ensure_team_name_is_available(self._repository, data.name)
        return Team.create(
            id=self._id_generator(),
            name=data.name,
            abbreviation=data.abbreviation,
            color=data.color,
            notes=data.notes,
        )
