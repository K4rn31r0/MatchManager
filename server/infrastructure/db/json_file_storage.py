"""Low-level access to the local JSON file that holds all application data."""

import json
import os
from pathlib import Path
from typing import Any


class JsonFileStorage:
    """Reads and writes a single JSON document on disk.

    Each repository owns one top-level key of the document, so several
    repositories can share the same file.
    """

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def read(self) -> dict[str, Any]:
        """Return the whole document, or an empty one if there is no file."""
        if not self._path.exists():
            return {}
        with self._path.open(encoding="utf-8") as file:
            return json.load(file)

    def write(self, document: dict[str, Any]) -> None:
        """Replace the whole document atomically."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._path.with_suffix(self._path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(document, file, ensure_ascii=False, indent=2)
        os.replace(temporary_path, self._path)
