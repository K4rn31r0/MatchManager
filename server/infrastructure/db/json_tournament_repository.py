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

    def get(self, tournament_id: str) -> Tournament | None:
        return next(
            (item for item in self.list_all() if item.id == tournament_id),
            None,
        )

    def update(self, tournament: Tournament) -> None:
        document = self._storage.read()
        document[_COLLECTION] = [
            {**record, **_to_record(tournament)}
            if record["id"] == tournament.id else record
            for record in document.get(_COLLECTION, [])
        ]
        self._storage.write(document)

    def delete(self, tournament_id: str) -> None:
        document = self._storage.read()
        for collection, key in (
            (_COLLECTION, "id"),
            ("registrations", "tournament_id"),
            ("matches", "tournament_id"),
        ):
            if collection in document:
                document[collection] = [
                    record for record in document[collection]
                    if record[key] != tournament_id
                ]
        self._storage.write(document)

    def participant_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self._storage.read().get("registrations", []):
            tournament_id = record["tournament_id"]
            counts[tournament_id] = counts.get(tournament_id, 0) + 1
        return counts

    def list_all(self) -> list[Tournament]:
        records = self._storage.read().get(_COLLECTION, [])
        return [_from_record(record) for record in records]


def _to_record(tournament: Tournament) -> dict[str, Any]:
    record = {
        "id": tournament.id,
        "name": tournament.name,
        "format": tournament.tournament_format.value,
        "status": tournament.status.value,
        "created_at": tournament.created_at.isoformat(),
        "modality": tournament.modality,
        "start_date": _date_to_text(tournament.start_date),
        "end_date": _date_to_text(tournament.end_date),
    }
    if tournament.updated_at is not None:
        record["updated_at"] = tournament.updated_at.isoformat()
    return record


def _from_record(record: dict[str, Any]) -> Tournament:
    return Tournament(
        id=record["id"],
        name=record["name"],
        tournament_format=TournamentFormat(record["format"]),
        status=TournamentStatus(record["status"]),
        created_at=datetime.fromisoformat(record["created_at"]),
        updated_at=(
            datetime.fromisoformat(record["updated_at"])
            if record.get("updated_at") else None
        ),
        modality=record.get("modality"),
        start_date=_text_to_date(record.get("start_date")),
        end_date=_text_to_date(record.get("end_date")),
    )


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _text_to_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value is not None else None
