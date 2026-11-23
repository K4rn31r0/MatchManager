import pytest

from server.core.entities.team import Team
from server.core.errors import TeamNotFoundError
from server.core.use_cases.get_team import GetTeam


def test_get_team_returns_the_requested_team(team_repository):
    team = Team.create(id="e1", name="Flamengo")
    team_repository.add(team)

    assert GetTeam(team_repository).execute("e1") == team


def test_get_team_rejects_unknown_id(team_repository):
    with pytest.raises(TeamNotFoundError):
        GetTeam(team_repository).execute("missing")
