"""Each JSON repository removes only its own records.

Deciding what else to remove (registrations, matches) is a business rule
that belongs to the DeleteTournament and DeleteTeam use cases.
"""

from datetime import datetime

from server.core.entities.match import Match
from server.core.entities.team import Team
from server.core.entities.tournament import Tournament, TournamentFormat
from server.infrastructure.db.json_file_storage import JsonFileStorage
from server.infrastructure.db.json_match_repository import JsonMatchRepository
from server.infrastructure.db.json_registration_repository import (
    JsonRegistrationRepository,
)
from server.infrastructure.db.json_team_repository import JsonTeamRepository
from server.infrastructure.db.json_tournament_repository import (
    JsonTournamentRepository,
)


def _tournament(tournament_id: str) -> Tournament:
    return Tournament.create_draft(
        id=tournament_id,
        name=f"Torneio {tournament_id}",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1, 12, 0),
    )


def _match(match_id: str, tournament_id: str) -> Match:
    return Match(
        id=match_id,
        tournament_id=tournament_id,
        round_number=1,
        first_team_id="e1",
        second_team_id="e2",
    )


def _seed(storage: JsonFileStorage) -> None:
    tournaments = JsonTournamentRepository(storage)
    teams = JsonTeamRepository(storage)
    registrations = JsonRegistrationRepository(storage)
    matches = JsonMatchRepository(storage)
    for tournament_id in ("copa", "liga"):
        tournaments.add(_tournament(tournament_id))
        matches.replace_for_tournament(
            tournament_id, [_match(f"{tournament_id}-1", tournament_id)]
        )
    for team_id in ("e1", "e2"):
        teams.add(Team.create(id=team_id, name=f"Equipe {team_id}"))
        registrations.add("copa", team_id)
    registrations.add("liga", "e1")


def test_tournament_delete_keeps_registrations_and_matches(tmp_path):
    storage = JsonFileStorage(tmp_path / "data.json")
    _seed(storage)

    JsonTournamentRepository(storage).delete("copa")

    assert JsonTournamentRepository(storage).get("copa") is None
    assert JsonRegistrationRepository(storage).team_ids("copa") == {
        "e1",
        "e2",
    }
    assert len(JsonMatchRepository(storage).list_for_tournament("copa")) == 1


def test_team_delete_keeps_registrations(tmp_path):
    storage = JsonFileStorage(tmp_path / "data.json")
    _seed(storage)

    JsonTeamRepository(storage).delete("e1")

    assert JsonTeamRepository(storage).get("e1") is None
    assert JsonRegistrationRepository(storage).team_ids("liga") == {"e1"}


def test_remove_all_registrations_of_a_tournament(tmp_path):
    storage = JsonFileStorage(tmp_path / "data.json")
    _seed(storage)
    registrations = JsonRegistrationRepository(storage)

    registrations.remove_all_for_tournament("copa")

    assert registrations.team_ids("copa") == set()
    assert registrations.team_ids("liga") == {"e1"}


def test_remove_all_registrations_of_a_team(tmp_path):
    storage = JsonFileStorage(tmp_path / "data.json")
    _seed(storage)
    registrations = JsonRegistrationRepository(storage)

    registrations.remove_all_for_team("e1")

    assert registrations.team_ids("copa") == {"e2"}
    assert registrations.team_ids("liga") == set()


def test_delete_matches_of_a_tournament(tmp_path):
    storage = JsonFileStorage(tmp_path / "data.json")
    _seed(storage)
    matches = JsonMatchRepository(storage)

    matches.delete_for_tournament("copa")

    assert matches.list_for_tournament("copa") == []
    assert matches.list_for_tournament("liga") == [_match("liga-1", "liga")]
