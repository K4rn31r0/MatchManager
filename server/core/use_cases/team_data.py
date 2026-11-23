"""Input data shared by the team creation and edition use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class TeamData:
    """Team fields provided by the user."""

    name: str
    abbreviation: str | None = None
    color: str | None = None
    notes: str | None = None
