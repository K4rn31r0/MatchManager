import pytest

from server.core.entities.team import Team
from server.core.errors import InvalidTeamError


def _team(name: str, abbreviation: str | None = None) -> Team:
    return Team.create(id="e1", name=name, abbreviation=abbreviation)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Flamengo", "FLA"),
        ("São Paulo Futebol Clube", "SAO"),
        ("Grêmio", "GRE"),
        ("Ação Esportiva", "ACA"),
        ("E.C. Bahia", "ECB"),
        ("1903 FC", "FC"),
        ("Ox", "OX"),
        ("atlético-mg", "ATL"),
    ],
)
def test_abbreviation_is_generated_from_first_three_letters_of_name(
    name, expected
):
    assert _team(name).abbreviation == expected


def test_name_without_letters_has_no_abbreviation():
    assert _team("1903").abbreviation is None


@pytest.mark.parametrize("blank", [None, "", "   "])
def test_blank_manual_abbreviation_falls_back_to_generated(blank):
    assert _team("Flamengo", abbreviation=blank).abbreviation == "FLA"


def test_manual_abbreviation_is_kept_as_typed():
    assert _team("Flamengo", abbreviation=" Mengão ").abbreviation == "Mengão"


@pytest.mark.parametrize("name", ["", "   "])
def test_team_requires_a_name(name):
    with pytest.raises(InvalidTeamError):
        _team(name)


def test_team_name_is_kept_as_typed_without_outer_spaces():
    assert _team("  Clube ATLÉTICO  ").name == "Clube ATLÉTICO"


@pytest.mark.parametrize("color", ["#1F6FEB", "#00ff00"])
def test_team_accepts_hex_color_and_stores_it_lowercase(color):
    team = Team.create(id="e1", name="Flamengo", color=color)

    assert team.color == color.lower()


@pytest.mark.parametrize("color", ["red", "#12345", "#gggggg", "1f6feb"])
def test_team_rejects_color_outside_hex_format(color):
    with pytest.raises(InvalidTeamError):
        Team.create(id="e1", name="Flamengo", color=color)


@pytest.mark.parametrize("blank", [None, "", "  "])
def test_blank_color_and_notes_are_treated_as_absent(blank):
    team = Team.create(id="e1", name="Flamengo", color=blank, notes=blank)

    assert team.color is None
    assert team.notes is None


def test_names_differing_only_in_case_or_accents_are_equivalent():
    team = _team("Grêmio")

    assert team.has_equivalent_name("  GREMIO ")
    assert not team.has_equivalent_name("Grêmio B")


def test_edit_returns_team_with_same_id_and_new_data():
    team = Team.create(id="e1", name="Flamengo", color="#ff0000")

    edited = team.edit(
        name="Fluminense", abbreviation="FLU", color=None, notes="Tricolor"
    )

    assert edited == Team(
        id="e1",
        name="Fluminense",
        abbreviation="FLU",
        color=None,
        notes="Tricolor",
    )
    assert team.name == "Flamengo"


def test_edit_with_blank_abbreviation_regenerates_it_from_new_name():
    team = _team("Flamengo", abbreviation="MENGO")

    edited = team.edit(
        name="Botafogo", abbreviation="", color=None, notes=None
    )

    assert edited.abbreviation == "BOT"
