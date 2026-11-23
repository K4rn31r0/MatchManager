"""Domain rules for comparing names."""

import unicodedata


def normalize_name(name: str) -> str:
    """Return a comparison key that ignores case, accents and outer spaces.

    "  Copa São Paulo " and "copa sao paulo" share the same key.
    """
    decomposed = unicodedata.normalize("NFKD", name.strip())
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return without_accents.casefold()
