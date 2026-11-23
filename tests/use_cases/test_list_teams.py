import pytest

from server.core.entities.team import Team
from server.core.use_cases.list_teams import ListTeams


@pytest.fixture
def list_teams(team_repository) -> ListTeams:
    for index, name in enumerate(
        ["São Paulo", "Botafogo", "Grêmio", "Paulista"], start=1
    ):
        team_repository.add(Team.create(id=f"e{index}", name=name))
    return ListTeams(team_repository)


def _names(teams: list[Team]) -> list[str]:
    return [team.name for team in teams]


def test_list_teams_returns_empty_list_when_none_exist(team_repository):
    assert ListTeams(team_repository).execute() == []


def test_list_teams_returns_all_teams_in_alphabetical_order(list_teams):
    assert _names(list_teams.execute()) == [
        "Botafogo",
        "Grêmio",
        "Paulista",
        "São Paulo",
    ]


@pytest.mark.parametrize("blank", [None, "", "   "])
def test_list_teams_with_blank_search_returns_all_teams(list_teams, blank):
    assert len(list_teams.execute(search=blank)) == 4


@pytest.mark.parametrize(
    ("search", "expected"),
    [
        ("paulo", ["São Paulo"]),
        ("  PAULO ", ["São Paulo"]),
        ("sao", ["São Paulo"]),
        ("gremio", ["Grêmio"]),
        ("Paul", ["Paulista", "São Paulo"]),
    ],
)
def test_list_teams_searches_part_of_name_ignoring_case_and_accents(
    list_teams, search, expected
):
    assert _names(list_teams.execute(search=search)) == expected


def test_list_teams_returns_empty_list_when_nothing_matches(list_teams):
    assert list_teams.execute(search="Corinthians") == []
