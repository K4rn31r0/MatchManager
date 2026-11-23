import pytest

from server.core.entities.team import Team
from server.core.errors import TeamInStartedTournamentError, TeamNotFoundError
from server.core.use_cases.delete_team import DeleteTeam
from tests.fakes import FakeTeamParticipationQuery


@pytest.fixture(autouse=True)
def teams(team_repository) -> None:
    team_repository.add(Team.create(id="e1", name="Flamengo"))
    team_repository.add(Team.create(id="e2", name="Grêmio"))


def test_delete_team_removes_only_that_team(team_repository):
    DeleteTeam(team_repository, FakeTeamParticipationQuery()).execute("e1")

    assert team_repository.get("e1") is None
    assert team_repository.get("e2") is not None


def test_delete_team_is_blocked_while_team_is_in_started_tournament(
    team_repository,
):
    participation = FakeTeamParticipationQuery({"e1"})

    with pytest.raises(TeamInStartedTournamentError):
        DeleteTeam(team_repository, participation).execute("e1")

    assert team_repository.get("e1") is not None


def test_delete_team_rejects_unknown_id(team_repository):
    with pytest.raises(TeamNotFoundError):
        DeleteTeam(team_repository, FakeTeamParticipationQuery()).execute(
            "missing"
        )
