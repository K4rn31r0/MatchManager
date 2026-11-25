import pytest

from server.core.entities.knockout_bracket import required_bye_count


@pytest.mark.parametrize(
    ("team_count", "expected"),
    [
        (2, 0),
        (3, 1),
        (4, 0),
        (5, 3),
        (6, 2),
        (8, 0),
        (9, 7),
    ],
)
def test_byes_complete_the_bracket_to_the_next_power_of_two(
    team_count, expected
):
    assert required_bye_count(team_count) == expected


@pytest.mark.parametrize("team_count", [0, 1])
def test_no_byes_without_enough_teams_for_a_bracket(team_count):
    assert required_bye_count(team_count) == 0
