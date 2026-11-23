"""Use case: list and search teams."""

from server.core.entities.names import normalize_name, optional_text
from server.core.entities.team import Team
from server.core.interfaces.team_repository import TeamRepository


class ListTeams:
    """Lists teams in alphabetical order, optionally filtered by name."""

    def __init__(self, repository: TeamRepository) -> None:
        self._repository = repository

    def execute(self, search: str | None = None) -> list[Team]:
        """Return the teams whose name contains ``search``.

        A blank search returns every team.
        """
        term = optional_text(search)
        teams = self._repository.list_all()
        if term is not None:
            teams = [team for team in teams if team.matches_search(term)]
        return sorted(teams, key=lambda team: normalize_name(team.name))
