import pytest

from server.core.errors import DuplicateTeamNameError, InvalidTeamError
from server.core.use_cases.create_team import CreateTeam
from server.core.use_cases.team_data import TeamData
from tests.fakes import SequentialIdGenerator


@pytest.fixture
def create_team(team_repository) -> CreateTeam:
    return CreateTeam(
        repository=team_repository,
        id_generator=SequentialIdGenerator(prefix="e"),
    )


def test_create_team_with_valid_data(create_team, team_repository):
    team = create_team.execute(
        TeamData(
            name="Flamengo",
            abbreviation="FLA",
            color="#ff0000",
            notes="Rubro-negro",
        )
    )

    assert team.id == "e1"
    assert team.name == "Flamengo"
    assert team.color == "#ff0000"
    assert team.notes == "Rubro-negro"
    assert team_repository.get("e1") == team


def test_create_team_generates_abbreviation_when_not_informed(create_team):
    team = create_team.execute(TeamData(name="São Paulo"))

    assert team.abbreviation == "SAO"


@pytest.mark.parametrize(
    "duplicate_name", ["Grêmio", "GRÊMIO", "gremio", "  Grêmio  "]
)
def test_create_team_rejects_duplicate_name_ignoring_case_and_accents(
    create_team, team_repository, duplicate_name
):
    create_team.execute(TeamData(name="Grêmio"))

    with pytest.raises(DuplicateTeamNameError):
        create_team.execute(TeamData(name=duplicate_name))

    assert len(team_repository.list_all()) == 1


def test_create_team_accepts_duplicate_abbreviation(
    create_team, team_repository
):
    create_team.execute(TeamData(name="Flamengo"))
    create_team.execute(TeamData(name="Flamengo B", abbreviation="FLA"))
    create_team.execute(TeamData(name="Flamenguinho"))

    abbreviations = [team.abbreviation for team in team_repository.list_all()]
    assert abbreviations == ["FLA", "FLA", "FLA"]


def test_create_team_rejects_empty_name(create_team, team_repository):
    with pytest.raises(InvalidTeamError):
        create_team.execute(TeamData(name="   "))

    assert team_repository.list_all() == []
