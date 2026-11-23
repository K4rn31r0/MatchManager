"""Application rule: team names must be unique."""

from server.core.errors import DuplicateTeamNameError
from server.core.interfaces.team_repository import TeamRepository


def ensure_team_name_is_available(
    repository: TeamRepository,
    name: str,
    ignored_team_id: str | None = None,
) -> None:
    """Raise DuplicateTeamNameError if another team uses an equivalent name.

    ``ignored_team_id`` lets a team keep its own name when it is edited.
    """
    for team in repository.list_all():
        if team.id != ignored_team_id and team.has_equivalent_name(name):
            raise DuplicateTeamNameError(
                f"Já existe uma equipe chamada “{team.name}”."
            )
