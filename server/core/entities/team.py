"""Team entity."""

import re
from dataclasses import dataclass

from server.core.entities.names import (
    normalize_name,
    optional_text,
    remove_accents,
)
from server.core.errors import InvalidTeamError

ABBREVIATION_LENGTH = 3
_HEX_COLOR = re.compile(r"#[0-9a-f]{6}")


@dataclass(frozen=True, kw_only=True)
class Team:
    """A team that can take part in any number of tournaments.

    Instances are immutable: domain operations return new instances.
    """

    id: str
    name: str
    abbreviation: str | None = None
    color: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidTeamError("O nome da equipe é obrigatório.")
        if self.color is not None and not _HEX_COLOR.fullmatch(self.color):
            raise InvalidTeamError(
                "A cor da equipe deve estar no formato #rrggbb."
            )

    @classmethod
    def create(
        cls,
        *,
        id: str,
        name: str,
        abbreviation: str | None = None,
        color: str | None = None,
        notes: str | None = None,
    ) -> "Team":
        """Create a team, generating the abbreviation when none is given.

        Surrounding whitespace is removed from text fields, blank optional
        fields are treated as absent and the color is stored in lower case.
        """
        return cls(
            id=id,
            name=name.strip(),
            abbreviation=(
                optional_text(abbreviation) or generate_abbreviation(name)
            ),
            color=_normalize_color(color),
            notes=optional_text(notes),
        )

    def edit(
        self,
        *,
        name: str,
        abbreviation: str | None,
        color: str | None,
        notes: str | None,
    ) -> "Team":
        """Return this team with new data, applying the creation rules."""
        return Team.create(
            id=self.id,
            name=name,
            abbreviation=abbreviation,
            color=color,
            notes=notes,
        )

    def has_equivalent_name(self, name: str) -> bool:
        """Tell whether a name clashes with this team's name.

        Names are equivalent when they differ only in case or accents.
        """
        return normalize_name(self.name) == normalize_name(name)

    def matches_search(self, term: str) -> bool:
        """Tell whether the name contains the term, ignoring case/accents."""
        return normalize_name(term) in normalize_name(self.name)


def generate_abbreviation(name: str) -> str | None:
    """Build an abbreviation from the first three letters of the name.

    Accents, punctuation, digits and spaces are ignored and the result is
    upper case: "São Paulo" -> "SAO", "E.C. Bahia" -> "ECB". Returns None
    when the name has no letters.
    """
    letters = [char for char in remove_accents(name) if char.isalpha()]
    return "".join(letters[:ABBREVIATION_LENGTH]).upper() or None


def _normalize_color(color: str | None) -> str | None:
    text = optional_text(color)
    return text.lower() if text is not None else None
