"""Listing, filtering and scheduling tournament matches (issue 10)."""

from dataclasses import replace
from datetime import date, datetime

import pytest

from server.core.entities.match import Match, MatchResult, MatchStatus
from server.core.entities.tournament import (
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError, TournamentNotFoundError
from server.core.use_cases.list_tournament_matches import (
    ListTournamentMatches,
    MatchFilter,
)
from server.core.use_cases.schedule_match import (
    MatchScheduleInput,
    ScheduleMatch,
)
from tests.fakes import InMemoryMatchRepository, InMemoryTournamentRepository


def make_tournament(status=TournamentStatus.IN_PROGRESS, tournament_id="t1"):
    return Tournament(
        id=tournament_id,
        name=f"Liga {tournament_id}",
        tournament_format=TournamentFormat.ROUND_ROBIN,
        status=status,
        created_at=datetime(2026, 1, 1),
    )


def make_match(match_id, round_number, status=MatchStatus.PENDING,
               tournament_id="t1"):
    return Match(
        id=match_id,
        tournament_id=tournament_id,
        round_number=round_number,
        first_team_id="a",
        second_team_id="b",
        status=status,
        result=(
            MatchResult.FIRST_WIN if status is MatchStatus.COMPLETED else None
        ),
    )


@pytest.fixture
def repositories():
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament())
    tournaments.add(make_tournament(tournament_id="other"))
    matches = InMemoryMatchRepository()
    matches.replace_for_tournament("t1", [
        make_match("m3", 2),
        make_match("m1", 1, MatchStatus.COMPLETED),
        make_match("m2", 1),
        make_match("m4", 2, MatchStatus.COMPLETED),
    ])
    matches.replace_for_tournament("other", [
        make_match("x1", 1, tournament_id="other"),
    ])
    return tournaments, matches


def ids(result):
    return [match.id for match in result.matches]


def test_list_matches_without_filter_orders_by_round(repositories):
    result = ListTournamentMatches(*repositories).execute("t1")

    assert ids(result) == ["m1", "m2", "m3", "m4"]
    assert result.rounds == (1, 2)
    assert result.total == 4


def test_list_matches_filters_by_round(repositories):
    result = ListTournamentMatches(*repositories).execute(
        "t1", MatchFilter(round_number=2),
    )

    assert ids(result) == ["m3", "m4"]
    assert result.rounds == (1, 2)


def test_list_matches_filters_by_status(repositories):
    result = ListTournamentMatches(*repositories).execute(
        "t1", MatchFilter(status=MatchStatus.PENDING),
    )

    assert ids(result) == ["m2", "m3"]


def test_list_matches_combines_round_and_status(repositories):
    result = ListTournamentMatches(*repositories).execute(
        "t1",
        MatchFilter(round_number=2, status=MatchStatus.COMPLETED),
    )

    assert ids(result) == ["m4"]
    assert result.total == 4
    assert result.pending == 2


def test_list_matches_returns_empty_for_unknown_round(repositories):
    result = ListTournamentMatches(*repositories).execute(
        "t1", MatchFilter(round_number=9),
    )

    assert result.matches == ()
    assert result.rounds == (1, 2)


def test_list_matches_orders_knockout_phase_by_bracket_position():
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament())
    matches = InMemoryMatchRepository()
    matches.replace_for_tournament("t1", [
        replace(make_match("b", 1), bracket_position=2),
        replace(make_match("a", 1), bracket_position=1),
    ])

    result = ListTournamentMatches(tournaments, matches).execute("t1")

    assert ids(result) == ["a", "b"]


def test_list_matches_rejects_unknown_tournament(repositories):
    with pytest.raises(TournamentNotFoundError):
        ListTournamentMatches(*repositories).execute("missing")


def test_schedule_match_sets_optional_date_and_location(repositories):
    tournaments, matches = repositories

    scheduled = ScheduleMatch(tournaments, matches).execute(
        "t1",
        "m2",
        MatchScheduleInput(
            scheduled_date=date(2026, 12, 5), location="  Ginásio  ",
        ),
    )

    assert scheduled.scheduled_date == date(2026, 12, 5)
    assert scheduled.location == "Ginásio"
    assert matches.get("m2") == scheduled
    assert scheduled.status is MatchStatus.PENDING


def test_schedule_match_clears_blank_values(repositories):
    tournaments, matches = repositories
    use_case = ScheduleMatch(tournaments, matches)
    use_case.execute(
        "t1", "m2",
        MatchScheduleInput(scheduled_date=date(2026, 12, 5), location="X"),
    )

    cleared = use_case.execute(
        "t1", "m2", MatchScheduleInput(scheduled_date=None, location="  "),
    )

    assert cleared.scheduled_date is None
    assert cleared.location is None


def test_schedule_does_not_change_a_recorded_result(repositories):
    tournaments, matches = repositories

    scheduled = ScheduleMatch(tournaments, matches).execute(
        "t1", "m1", MatchScheduleInput(location="Estádio"),
    )

    assert scheduled.status is MatchStatus.COMPLETED
    assert scheduled.result is MatchResult.FIRST_WIN


def test_result_can_be_recorded_without_date_or_location():
    match = make_match("m1", 1)

    recorded = match.record_result(
        result=MatchResult.DRAW,
        first_score=None,
        second_score=None,
        first_team_stats=None,
        second_team_stats=None,
    )

    assert recorded.status is MatchStatus.COMPLETED
    assert recorded.scheduled_date is None and recorded.location is None


def test_recording_result_keeps_the_schedule():
    match = make_match("m1", 1).schedule(
        scheduled_date=date(2026, 12, 5), location="Estádio",
    )

    recorded = match.record_result(
        result=MatchResult.FIRST_WIN,
        first_score=1,
        second_score=0,
        first_team_stats=None,
        second_team_stats=None,
    )

    assert recorded.scheduled_date == date(2026, 12, 5)
    assert recorded.location == "Estádio"


def test_schedule_match_rejects_draft_tournament(repositories):
    tournaments, matches = repositories
    tournaments.update(make_tournament(TournamentStatus.DRAFT))

    with pytest.raises(InvalidTournamentError, match="iniciados"):
        ScheduleMatch(tournaments, matches).execute(
            "t1", "m2", MatchScheduleInput(location="Estádio"),
        )

    assert matches.get("m2").location is None


def test_schedule_match_rejects_match_from_another_tournament(repositories):
    tournaments, matches = repositories

    with pytest.raises(InvalidTournamentError, match="Partida não encontrada"):
        ScheduleMatch(tournaments, matches).execute(
            "t1", "x1", MatchScheduleInput(location="Estádio"),
        )
