from datetime import date

from server.core.entities.match import Match, MatchResult, MatchStatus
from server.infrastructure.db.json_file_storage import JsonFileStorage
from server.infrastructure.db.json_match_repository import JsonMatchRepository


def test_match_result_statistics_and_correction_round_trip(tmp_path):
    path = tmp_path / "data.json"
    repository = JsonMatchRepository(JsonFileStorage(path))
    match = Match(
        id="m1",
        tournament_id="t1",
        round_number=1,
        first_team_id="a",
        second_team_id="b",
        status=MatchStatus.COMPLETED,
        result=MatchResult.FIRST_WIN,
        first_score=2,
        second_score=1,
        first_team_stats={"Gols": 2, "Faltas": 4},
        second_team_stats={"Gols": 1},
    )

    repository.replace_for_tournament("t1", [match])

    assert repository.get("m1") == match
    assert repository.list_for_tournament("t1") == [match]

    corrected = match.record_result(
        result=MatchResult.DRAW,
        first_score=1,
        second_score=1,
        first_team_stats={"Gols": 1},
        second_team_stats={"Gols": 1},
    )
    repository.update(corrected)

    assert repository.get("m1") == corrected


def test_match_schedule_round_trip_and_absent_fields(tmp_path):
    path = tmp_path / "data.json"
    repository = JsonMatchRepository(JsonFileStorage(path))
    match = Match(
        id="m1",
        tournament_id="t1",
        round_number=1,
        first_team_id="a",
        second_team_id="b",
    )
    repository.replace_for_tournament("t1", [match])
    assert repository.get("m1").scheduled_date is None
    assert repository.get("m1").location is None

    scheduled = match.schedule(
        scheduled_date=date(2026, 12, 5),
        location="Ginásio Central",
    )
    repository.update(scheduled)

    assert repository.get("m1") == scheduled
