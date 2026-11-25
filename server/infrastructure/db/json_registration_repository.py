"""Store registrations in the shared local JSON document."""

from server.core.entities.team import Team
from server.core.entities.tournament import TournamentStatus
from server.core.interfaces.team_participation_query import (
    TeamParticipationQuery,
)
from server.infrastructure.db.json_file_storage import JsonFileStorage
from server.infrastructure.db.json_team_repository import team_to_record


class JsonRegistrationRepository(TeamParticipationQuery):
    def __init__(self, storage: JsonFileStorage) -> None:
        self._storage = storage

    def team_ids(self, tournament_id: str) -> set[str]:
        return {
            record["team_id"]
            for record in self._storage.read().get("registrations", [])
            if record["tournament_id"] == tournament_id
        }

    def add(self, tournament_id: str, team_id: str) -> None:
        document = self._storage.read()
        document.setdefault("registrations", []).append(
            {"tournament_id": tournament_id, "team_id": team_id}
        )
        self._storage.write(document)

    def add_new_team(self, tournament_id: str, team: Team) -> None:
        document = self._storage.read()
        document.setdefault("teams", []).append(team_to_record(team))
        document.setdefault("registrations", []).append(
            {"tournament_id": tournament_id, "team_id": team.id}
        )
        self._storage.write(document)

    def remove(self, tournament_id: str, team_id: str) -> None:
        document = self._storage.read()
        document["registrations"] = [
            record
            for record in document.get("registrations", [])
            if (record["tournament_id"], record["team_id"])
            != (tournament_id, team_id)
        ]
        self._storage.write(document)

    def remove_all_for_tournament(self, tournament_id: str) -> None:
        self._remove_where("tournament_id", tournament_id)

    def remove_all_for_team(self, team_id: str) -> None:
        self._remove_where("team_id", team_id)

    def _remove_where(self, field: str, value: str) -> None:
        document = self._storage.read()
        document["registrations"] = [
            record
            for record in document.get("registrations", [])
            if record[field] != value
        ]
        self._storage.write(document)

    def is_in_started_tournament(self, team_id: str) -> bool:
        document = self._storage.read()
        started = {
            record["id"]
            for record in document.get("tournaments", [])
            if record["status"] != TournamentStatus.DRAFT.value
        }
        return any(
            record["team_id"] == team_id and record["tournament_id"] in started
            for record in document.get("registrations", [])
        )
