"""Domain rules for handling names and free text typed by the user."""

import unicodedata


def remove_accents(text: str) -> str:
    """Return the text without diacritics: "São Grêmio" -> "Sao Gremio"."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )


def normalize_name(name: str) -> str:
    """Return a comparison key that ignores case, accents and outer spaces.

    "  Copa São Paulo " and "copa sao paulo" share the same key.
    """
    return remove_accents(name.strip()).casefold()


def optional_text(value: str | None) -> str | None:
    """Return the stripped text, or None when it is missing or blank."""
    if value is None or not value.strip():
        return None
    return value.strip()
