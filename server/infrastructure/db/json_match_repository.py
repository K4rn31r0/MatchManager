"""Persist tournament matches in the shared local JSON document."""

from typing import Any

from server.core.entities.match import Match, MatchStatus
from server.infrastructure.db.json_file_storage import JsonFileStorage


class JsonMatchRepository:
    def __init__(self, storage: JsonFileStorage) -> None:
        self._storage = storage

    def replace_for_tournament(
        self,
        tournament_id: str,
        matches: list[Match],
    ) -> None:
        document = self._storage.read()
        remaining = [
            record for record in document.get("matches", [])
            if record.get("tournament_id") != tournament_id
        ]
        document["matches"] = remaining + [
            _to_record(match) for match in matches
        ]
        self._storage.write(document)


def _to_record(match: Match) -> dict[str, Any]:
    return {
        "id": match.id,
        "tournament_id": match.tournament_id,
        "round": match.round_number,
        "first_team_id": match.first_team_id,
        "second_team_id": match.second_team_id,
        "status": match.status.value,
    }
