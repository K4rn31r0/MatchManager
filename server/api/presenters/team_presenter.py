"""Formats teams for display in the HTML templates."""

from dataclasses import dataclass

from server.core.entities.team import Team

_NO_ABBREVIATION = "—"


@dataclass(frozen=True)
class TeamViewModel:
    """Display-ready representation of a team."""

    id: str
    name: str
    abbreviation: str
    color: str | None
    notes: str | None


def present_team(team: Team) -> TeamViewModel:
    return TeamViewModel(
        id=team.id,
        name=team.name,
        abbreviation=team.abbreviation or _NO_ABBREVIATION,
        color=team.color,
        notes=team.notes,
    )


def present_teams(teams: list[Team]) -> list[TeamViewModel]:
    return [present_team(team) for team in teams]


def team_form_values(team: Team) -> dict[str, str]:
    """Return the team data as values to pre-fill the edit form."""
    return {
        "name": team.name,
        "abbreviation": team.abbreviation or "",
        "has_color": "on" if team.color else "",
        "color": team.color or "#1f6feb",
        "notes": team.notes or "",
    }
