"""Use case: edit a team."""

from server.core.entities.team import Team
from server.core.interfaces.team_repository import TeamRepository
from server.core.use_cases.get_team import require_team
from server.core.use_cases.team_data import TeamData
from server.core.use_cases.team_name_availability import (
    ensure_team_name_is_available,
)


class UpdateTeam:
    """Updates a team's data, keeping its name unique."""

    def __init__(self, repository: TeamRepository) -> None:
        self._repository = repository

    def execute(self, team_id: str, data: TeamData) -> Team:
        """Apply the new data to the team and persist it.

        Raises:
            TeamNotFoundError: no team has the given id.
            InvalidTeamError: the data breaks a team invariant.
            DuplicateTeamNameError: another team uses the name.
        """
        team = require_team(self._repository, team_id)
        ensure_team_name_is_available(
            self._repository, data.name, ignored_team_id=team.id
        )
        updated = team.edit(
            name=data.name,
            abbreviation=data.abbreviation,
            color=data.color,
            notes=data.notes,
        )
        self._repository.update(updated)
        return updated
