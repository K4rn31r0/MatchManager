from datetime import datetime

from server.core.entities.team import Team
from server.core.entities.tournament import Tournament, TournamentFormat
from server.infrastructure.db.json_file_storage import JsonFileStorage
from server.infrastructure.db.json_team_repository import JsonTeamRepository
from server.infrastructure.db.json_tournament_repository import (
    JsonTournamentRepository,
)


def _repository(path) -> JsonTeamRepository:
    return JsonTeamRepository(JsonFileStorage(path))


def _full_team() -> Team:
    return Team.create(
        id="e1",
        name="Grêmio",
        abbreviation="GRE",
        color="#0d80bf",
        notes="Tricolor gaúcho",
    )


def test_list_all_is_empty_when_file_does_not_exist(tmp_path):
    assert _repository(tmp_path / "data.json").list_all() == []


def test_added_team_is_recovered_by_a_new_repository_instance(tmp_path):
    path = tmp_path / "data.json"
    team = _full_team()

    _repository(path).add(team)

    assert _repository(path).get("e1") == team
    assert _repository(path).list_all() == [team]


def test_team_without_optional_fields_round_trips(tmp_path):
    path = tmp_path / "data.json"
    team = Team.create(id="e1", name="1903")

    _repository(path).add(team)

    assert _repository(path).get("e1") == team


def test_get_returns_none_for_unknown_id(tmp_path):
    repository = _repository(tmp_path / "data.json")
    repository.add(_full_team())

    assert repository.get("missing") is None


def test_update_replaces_only_the_team_with_same_id(tmp_path):
    path = tmp_path / "data.json"
    repository = _repository(path)
    repository.add(_full_team())
    repository.add(Team.create(id="e2", name="Internacional"))

    edited = _full_team().edit(
        name="Grêmio FBPA", abbreviation=None, color=None, notes=None
    )
    repository.update(edited)

    assert _repository(path).list_all() == [
        edited,
        Team.create(id="e2", name="Internacional"),
    ]


def test_delete_removes_only_the_team_with_same_id(tmp_path):
    path = tmp_path / "data.json"
    repository = _repository(path)
    repository.add(_full_team())
    repository.add(Team.create(id="e2", name="Internacional"))

    repository.delete("e1")

    assert _repository(path).list_all() == [
        Team.create(id="e2", name="Internacional")
    ]


def test_teams_and_tournaments_share_the_same_file_without_conflict(
    tmp_path,
):
    storage = JsonFileStorage(tmp_path / "data.json")
    tournaments = JsonTournamentRepository(storage)
    teams = JsonTeamRepository(storage)
    tournament = Tournament.create_draft(
        id="t1",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1, 12, 0),
    )

    tournaments.add(tournament)
    teams.add(_full_team())
    teams.delete("e1")

    assert tournaments.list_all() == [tournament]
    assert teams.list_all() == []
