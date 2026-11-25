"""Team repository backed by the local JSON file."""

from typing import Any

from server.core.entities.team import Team
from server.core.interfaces.team_repository import TeamRepository
from server.infrastructure.db.json_file_storage import JsonFileStorage

_COLLECTION = "teams"


class JsonTeamRepository(TeamRepository):
    """Persists teams under the "teams" key of the JSON file."""

    def __init__(self, storage: JsonFileStorage) -> None:
        self._storage = storage

    def add(self, team: Team) -> None:
        document = self._storage.read()
        document.setdefault(_COLLECTION, []).append(team_to_record(team))
        self._storage.write(document)

    def get(self, team_id: str) -> Team | None:
        for record in self._records(self._storage.read()):
            if record["id"] == team_id:
                return _from_record(record)
        return None

    def update(self, team: Team) -> None:
        document = self._storage.read()
        document[_COLLECTION] = [
            team_to_record(team) if record["id"] == team.id else record
            for record in self._records(document)
        ]
        self._storage.write(document)

    def delete(self, team_id: str) -> None:
        document = self._storage.read()
        document[_COLLECTION] = [
            record
            for record in self._records(document)
            if record["id"] != team_id
        ]
        self._storage.write(document)

    def list_all(self) -> list[Team]:
        return [
            _from_record(record)
            for record in self._records(self._storage.read())
        ]

    @staticmethod
    def _records(document: dict[str, Any]) -> list[dict[str, Any]]:
        return document.get(_COLLECTION, [])


def team_to_record(team: Team) -> dict[str, Any]:
    return {
        "id": team.id,
        "name": team.name,
        "abbreviation": team.abbreviation,
        "color": team.color,
        "notes": team.notes,
    }


def _from_record(record: dict[str, Any]) -> Team:
    return Team(
        id=record["id"],
        name=record["name"],
        abbreviation=record.get("abbreviation"),
        color=record.get("color"),
        notes=record.get("notes"),
    )
