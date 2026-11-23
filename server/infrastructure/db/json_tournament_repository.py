"""Tournament repository backed by the local JSON file."""

from datetime import date, datetime
from typing import Any

from server.core.entities.tournament import (
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.interfaces.tournament_repository import TournamentRepository
from server.infrastructure.db.json_file_storage import JsonFileStorage

_COLLECTION = "tournaments"


class JsonTournamentRepository(TournamentRepository):
    """Persists tournaments under the "tournaments" key of the JSON file."""

    def __init__(self, storage: JsonFileStorage) -> None:
        self._storage = storage

    def add(self, tournament: Tournament) -> None:
        document = self._storage.read()
        document.setdefault(_COLLECTION, []).append(_to_record(tournament))
        self._storage.write(document)

    def list_all(self) -> list[Tournament]:
        records = self._storage.read().get(_COLLECTION, [])
        return [_from_record(record) for record in records]


def _to_record(tournament: Tournament) -> dict[str, Any]:
    return {
        "id": tournament.id,
        "name": tournament.name,
        "format": tournament.tournament_format.value,
        "status": tournament.status.value,
        "created_at": tournament.created_at.isoformat(),
        "modality": tournament.modality,
        "start_date": _date_to_text(tournament.start_date),
        "end_date": _date_to_text(tournament.end_date),
    }


def _from_record(record: dict[str, Any]) -> Tournament:
    return Tournament(
        id=record["id"],
        name=record["name"],
        tournament_format=TournamentFormat(record["format"]),
        status=TournamentStatus(record["status"]),
        created_at=datetime.fromisoformat(record["created_at"]),
        modality=record.get("modality"),
        start_date=_text_to_date(record.get("start_date")),
        end_date=_text_to_date(record.get("end_date")),
    )


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _text_to_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value is not None else None
