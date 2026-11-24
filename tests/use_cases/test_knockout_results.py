from datetime import datetime

import pytest

from server.core.entities.match import Match, MatchResult, MatchStatus
from server.core.entities.tournament import (
    KnockoutByeStrategy,
    KnockoutConfig,
    KnockoutOrderMode,
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError
from server.core.use_cases.record_knockout_result import (
    KnockoutResultInput,
    RecordKnockoutResult,
)
from server.core.use_cases.finish_knockout_tournament import (
    FinishKnockoutTournament,
)
from tests.fakes import InMemoryTournamentRepository


class InMemoryMatches:
    def __init__(self, matches=()):
        self.items = {match.id: match for match in matches}

    def get(self, match_id):
        return self.items.get(match_id)

    def list_for_tournament(self, tournament_id):
        return [
            match for match in self.items.values()
            if match.tournament_id == tournament_id
        ]

    def update(self, match):
        self.items[match.id] = match

    def replace_for_tournament(self, tournament_id, matches):
        self.items = {
            match_id: match
            for match_id, match in self.items.items()
            if match.tournament_id != tournament_id
        }
        self.items.update({match.id: match for match in matches})


def make_tournament(team_ids=("a", "b")):
    return Tournament(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        status=TournamentStatus.IN_PROGRESS,
        created_at=datetime(2026, 1, 1),
        knockout=KnockoutConfig(
            order_mode=KnockoutOrderMode.MANUAL,
            initial_order=team_ids,
            bye_strategy=KnockoutByeStrategy.PERFORMANCE,
            bye_team_ids=(),
        ),
    )


def make_match(
    *,
    tournament_id="cup",
    match_id="m1",
    round_number=1,
    bracket_position=1,
    first_team_id="a",
    second_team_id="b",
    status=MatchStatus.PENDING,
    result=None,
):
    return Match(
        id=match_id,
        tournament_id=tournament_id,
        round_number=round_number,
        bracket_position=bracket_position,
        first_team_id=first_team_id,
        second_team_id=second_team_id,
        status=status,
        result=result,
    )


def make_use_case(matches):
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament())
    return RecordKnockoutResult(tournaments, matches), tournaments


def test_record_knockout_winner_directly_without_score():
    matches = InMemoryMatches([make_match()])
    use_case, _ = make_use_case(matches)

    recorded = use_case.execute(
        "cup",
        "m1",
        KnockoutResultInput(result=MatchResult.SECOND_WIN),
    )

    assert recorded.status is MatchStatus.COMPLETED
    assert recorded.result is MatchResult.SECOND_WIN
    assert recorded.first_score is None
    assert recorded.second_score is None
    assert matches.get("m1") == recorded


def test_record_knockout_winner_with_valid_score():
    matches = InMemoryMatches([make_match()])
    use_case, _ = make_use_case(matches)

    recorded = use_case.execute(
        "cup",
        "m1",
        KnockoutResultInput(
            result=MatchResult.FIRST_WIN,
            first_score=2,
            second_score=1,
        ),
    )

    assert recorded.result is MatchResult.FIRST_WIN
    assert (recorded.first_score, recorded.second_score) == (2, 1)


@pytest.mark.parametrize(
    ("result", "first_score", "second_score", "message"),
    [
        (None, None, None, "vencedor"),
        (MatchResult.DRAW, None, None, "vencedor"),
        (MatchResult.FIRST_WIN, 2, None, "placar completo"),
        (MatchResult.SECOND_WIN, None, 1, "placar completo"),
        (MatchResult.FIRST_WIN, 1, 1, "placar não corresponde"),
    ],
)
def test_knockout_rejects_missing_winner_draw_and_invalid_scores(
    result,
    first_score,
    second_score,
    message,
):
    matches = InMemoryMatches([make_match()])
    use_case, _ = make_use_case(matches)

    with pytest.raises(InvalidTournamentError, match=message):
        use_case.execute(
            "cup",
            "m1",
            KnockoutResultInput(
                result=result,
                first_score=first_score,
                second_score=second_score,
            ),
        )

    assert matches.get("m1").status is MatchStatus.PENDING


def test_knockout_winner_advances_into_the_next_match():
    matches = InMemoryMatches([
        make_match(match_id="m1", bracket_position=1),
        make_match(
            match_id="m2",
            bracket_position=2,
            first_team_id="c",
            second_team_id="d",
        ),
        make_match(
            match_id="final",
            round_number=2,
            first_team_id=None,
            second_team_id=None,
        ),
    ])
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament(("a", "b", "c", "d")))
    use_case = RecordKnockoutResult(tournaments, matches)

    use_case.execute(
        "cup",
        "m1",
        KnockoutResultInput(result=MatchResult.FIRST_WIN),
    )

    assert matches.get("final").first_team_id == "a"
    assert matches.get("final").second_team_id is None


def test_correcting_knockout_result_updates_next_match_before_it_is_played():
    matches = InMemoryMatches([
        make_match(
            match_id="m1",
            bracket_position=1,
            status=MatchStatus.COMPLETED,
            result=MatchResult.FIRST_WIN,
        ),
        make_match(
            match_id="m2",
            bracket_position=2,
            first_team_id="c",
            second_team_id="d",
        ),
        make_match(
            match_id="final",
            round_number=2,
            first_team_id="a",
            second_team_id=None,
        ),
    ])
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament(("a", "b", "c", "d")))

    recorded = RecordKnockoutResult(tournaments, matches).execute(
        "cup",
        "m1",
        KnockoutResultInput(result=MatchResult.SECOND_WIN),
    )

    assert recorded.result is MatchResult.SECOND_WIN
    assert matches.get("final").first_team_id == "b"


def test_knockout_result_cannot_be_corrected_after_a_subsequent_match():
    matches = InMemoryMatches([
        make_match(
            match_id="m1",
            bracket_position=1,
            status=MatchStatus.COMPLETED,
            result=MatchResult.FIRST_WIN,
        ),
        make_match(
            match_id="m2",
            bracket_position=2,
            first_team_id="c",
            second_team_id="d",
        ),
        make_match(
            match_id="final",
            round_number=2,
            first_team_id="a",
            second_team_id="c",
            status=MatchStatus.COMPLETED,
            result=MatchResult.FIRST_WIN,
        ),
    ])
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament(("a", "b", "c", "d")))

    with pytest.raises(InvalidTournamentError, match="partida subsequente"):
        RecordKnockoutResult(tournaments, matches).execute(
            "cup",
            "m1",
            KnockoutResultInput(result=MatchResult.SECOND_WIN),
        )

    assert matches.get("m1").result is MatchResult.FIRST_WIN


def test_finish_knockout_rejects_pending_matches():
    matches = InMemoryMatches([make_match()])
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament())

    with pytest.raises(InvalidTournamentError, match="partidas pendentes"):
        FinishKnockoutTournament(tournaments, matches).execute("cup")


def test_finish_knockout_rejects_completed_match_without_winner():
    matches = InMemoryMatches([
        make_match(status=MatchStatus.COMPLETED, result=None),
    ])
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament())

    with pytest.raises(InvalidTournamentError, match="sem vencedor"):
        FinishKnockoutTournament(tournaments, matches).execute("cup")

    assert tournaments.get("cup").status is TournamentStatus.IN_PROGRESS


def test_finish_knockout_sets_finished_after_the_final_result():
    final = make_match(
        round_number=1,
        status=MatchStatus.COMPLETED,
        result=MatchResult.SECOND_WIN,
    )
    matches = InMemoryMatches([final])
    tournaments = InMemoryTournamentRepository()
    tournaments.add(make_tournament())

    finished = FinishKnockoutTournament(
        tournaments,
        matches,
        clock=lambda: datetime(2026, 1, 2),
    ).execute("cup")

    assert finished.status is TournamentStatus.FINISHED
    assert tournaments.get("cup").status is TournamentStatus.FINISHED
