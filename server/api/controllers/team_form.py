"""Parse HTML form data for a team."""

from collections.abc import Mapping

from server.core.use_cases.team_data import TeamData


def parse_team_form(form: Mapping[str, str]) -> TeamData:
    return TeamData(
        name=form.get("name", ""),
        abbreviation=form.get("abbreviation"),
        color=form.get("color") if form.get("has_color") else None,
        notes=form.get("notes"),
    )
