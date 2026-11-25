"""Persist tournament matches in the shared local JSON document."""

from datetime import date
from typing import Any

from server.core.entities.match import Match, MatchResult, MatchStatus
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
            record
            for record in document.get("matches", [])
            if record.get("tournament_id") != tournament_id
        ]
        document["matches"] = remaining + [
            _to_record(match) for match in matches
        ]
        self._storage.write(document)

    def get(self, match_id: str) -> Match | None:
        for record in self._storage.read().get("matches", []):
            if record.get("id") == match_id:
                match = _from_record(record)
                return match
        return None

    def list_for_tournament(self, tournament_id: str) -> list[Match]:
        matches: list[Match] = []
        for record in self._storage.read().get("matches", []):
            if record.get("tournament_id") != tournament_id:
                continue
            match = _from_record(record)
            if match is not None:
                matches.append(match)
        return matches

    def update(self, match: Match) -> None:
        document = self._storage.read()
        document["matches"] = [
            _to_record(match) if record.get("id") == match.id else record
            for record in document.get("matches", [])
        ]
        self._storage.write(document)


def _to_record(match: Match) -> dict[str, Any]:
    record = {
        "id": match.id,
        "tournament_id": match.tournament_id,
        "round": match.round_number,
        "first_team_id": match.first_team_id,
        "second_team_id": match.second_team_id,
        "status": match.status.value,
    }
    if match.result is not None:
        record["result"] = match.result.value
    if match.first_score is not None:
        record["first_score"] = match.first_score
    if match.second_score is not None:
        record["second_score"] = match.second_score
    if match.first_team_stats is not None:
        record["first_team_stats"] = match.first_team_stats
    if match.second_team_stats is not None:
        record["second_team_stats"] = match.second_team_stats
    if match.bracket_position is not None:
        record["bracket_position"] = match.bracket_position
    if match.scheduled_date is not None:
        record["scheduled_date"] = match.scheduled_date.isoformat()
    if match.location is not None:
        record["location"] = match.location
    return record


def _from_record(record: dict[str, Any]) -> Match | None:
    required = (
        "id",
        "tournament_id",
        "round",
        "first_team_id",
        "second_team_id",
        "status",
    )
    if any(key not in record for key in required):
        return None
    return Match(
        id=record["id"],
        tournament_id=record["tournament_id"],
        round_number=record["round"],
        first_team_id=record["first_team_id"],
        second_team_id=record["second_team_id"],
        bracket_position=record.get("bracket_position"),
        status=MatchStatus(record["status"]),
        result=(
            MatchResult(record["result"])
            if record.get("result") is not None
            else None
        ),
        first_score=record.get("first_score"),
        second_score=record.get("second_score"),
        first_team_stats=record.get("first_team_stats"),
        second_team_stats=record.get("second_team_stats"),
        scheduled_date=(
            date.fromisoformat(record["scheduled_date"])
            if record.get("scheduled_date")
            else None
        ),
        location=record.get("location"),
    )
