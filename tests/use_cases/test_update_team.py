import pytest

from server.core.entities.team import Team
from server.core.errors import (
    DuplicateTeamNameError,
    InvalidTeamError,
    TeamNotFoundError,
)
from server.core.use_cases.team_data import TeamData
from server.core.use_cases.update_team import UpdateTeam


@pytest.fixture
def update_team(team_repository) -> UpdateTeam:
    team_repository.add(Team.create(id="e1", name="Flamengo"))
    team_repository.add(Team.create(id="e2", name="Grêmio"))
    return UpdateTeam(team_repository)


def test_update_team_changes_every_field(update_team, team_repository):
    updated = update_team.execute(
        "e1",
        TeamData(
            name="Fluminense",
            abbreviation="FLU",
            color="#7a0019",
            notes="Tricolor carioca",
        ),
    )

    assert (
        team_repository.get("e1")
        == updated
        == Team(
            id="e1",
            name="Fluminense",
            abbreviation="FLU",
            color="#7a0019",
            notes="Tricolor carioca",
        )
    )


def test_update_team_can_keep_its_own_name_with_different_case(
    update_team, team_repository
):
    update_team.execute("e1", TeamData(name="FLAMENGO", abbreviation="MEN"))

    assert team_repository.get("e1").name == "FLAMENGO"
    assert team_repository.get("e1").abbreviation == "MEN"


def test_update_team_rejects_name_of_another_team(
    update_team, team_repository
):
    with pytest.raises(DuplicateTeamNameError):
        update_team.execute("e1", TeamData(name="gremio"))

    assert team_repository.get("e1").name == "Flamengo"


def test_update_team_rejects_invalid_data(update_team, team_repository):
    with pytest.raises(InvalidTeamError):
        update_team.execute("e1", TeamData(name="Flamengo", color="red"))

    assert team_repository.get("e1").color is None


def test_update_team_rejects_unknown_id(update_team):
    with pytest.raises(TeamNotFoundError):
        update_team.execute("missing", TeamData(name="Vasco"))
