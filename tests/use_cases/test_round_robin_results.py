from dataclasses import replace
from datetime import datetime

import pytest

from server.core.entities.match import Match, MatchResult, MatchStatus
from server.core.entities.team import Team
from server.core.entities.tournament import (
    RoundRobinConfig,
    RoundRobinMode,
    TieBreaker,
    TieBreakerDirection,
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError
from server.core.use_cases.calculate_round_robin_standings import (
    CalculateRoundRobinStandings,
)
from server.core.use_cases.record_round_robin_result import (
    RecordRoundRobinResult,
    RoundRobinResultInput,
)
from server.core.use_cases.finish_round_robin_tournament import (
    FinishRoundRobinTournament,
)
from tests.fakes import InMemoryTeamRepository, InMemoryTournamentRepository


class InMemoryMatches:
    def __init__(self, matches=()):
        self.items = {match.id: match for match in matches}

    def replace_for_tournament(self, tournament_id, matches):
        for match_id in [
            key for key, match in self.items.items()
            if match.tournament_id == tournament_id
        ]:
            del self.items[match_id]
        for match in matches:
            self.items[match.id] = match

    def get(self, match_id):
        return self.items.get(match_id)

    def list_for_tournament(self, tournament_id):
        return [
            match for match in self.items.values()
            if match.tournament_id == tournament_id
        ]

    def update(self, match):
        self.items[match.id] = match


class InMemoryRegistrations:
    def __init__(self, team_ids):
        self.team_ids_by_tournament = team_ids

    def team_ids(self, tournament_id):
        return set(self.team_ids_by_tournament)


def make_tournament(match_status=TournamentStatus.IN_PROGRESS):
    config = RoundRobinConfig(
        mode=RoundRobinMode.SINGLE,
        win_points=3,
        draw_points=1,
        loss_points=0,
        tie_breakers=(
            TieBreaker(name="Saldo", direction=TieBreakerDirection.POSITIVE),
        ),
        statistic_fields=(),
    )
    return Tournament(
        id="t1",
        name="Liga",
        tournament_format=TournamentFormat.ROUND_ROBIN,
        status=match_status,
        created_at=datetime(2026, 1, 1),
        round_robin=config,
    )


def make_teams():
    teams = InMemoryTeamRepository()
    teams.add(Team.create(id="a", name="Águias"))
    teams.add(Team.create(id="b", name="Tigres"))
    teams.add(Team.create(id="c", name="Leões"))
    return teams


def test_record_direct_result_completes_match():
    tournament_repository = InMemoryTournamentRepository()
    tournament = make_tournament()
    tournament_repository.add(tournament)
    match = Match(
        id="m1",
        tournament_id="t1",
        round_number=1,
        first_team_id="a",
        second_team_id="b",
    )
    matches = InMemoryMatches([match])

    result = RecordRoundRobinResult(
        tournament_repository,
        matches,
    ).execute(
        "t1",
        "m1",
        RoundRobinResultInput(result=MatchResult.FIRST_WIN),
    )

    assert result.status is MatchStatus.COMPLETED
    assert result.result is MatchResult.FIRST_WIN
    assert result.first_score is None
    assert result.second_score is None


@pytest.mark.parametrize(
    "score",
    [
        {"first_score": 1, "second_score": None},
        {"first_score": None, "second_score": 0},
    ],
)
def test_record_result_rejects_partial_score(score):
    tournament_repository = InMemoryTournamentRepository()
    tournament_repository.add(make_tournament())
    match = Match(
        id="m1",
        tournament_id="t1",
        round_number=1,
        first_team_id="a",
        second_team_id="b",
    )
    matches = InMemoryMatches([match])

    with pytest.raises(InvalidTournamentError, match="placar completo"):
        RecordRoundRobinResult(tournament_repository, matches).execute(
            "t1",
            "m1",
            RoundRobinResultInput(
                result=MatchResult.FIRST_WIN,
                **score,
            ),
        )


def test_score_must_agree_with_direct_result():
    tournament_repository = InMemoryTournamentRepository()
    tournament_repository.add(make_tournament())
    match = Match(
        id="m1",
        tournament_id="t1",
        round_number=1,
        first_team_id="a",
        second_team_id="b",
    )
    matches = InMemoryMatches([match])

    with pytest.raises(InvalidTournamentError, match="placar.*resultado"):
        RecordRoundRobinResult(tournament_repository, matches).execute(
            "t1",
            "m1",
            RoundRobinResultInput(
                result=MatchResult.FIRST_WIN,
                first_score=0,
                second_score=1,
            ),
        )


def test_calculation_applies_points_and_alphabetical_final_tiebreak():
    tournament_repository = InMemoryTournamentRepository()
    tournament = make_tournament()
    tournament_repository.add(tournament)
    teams = make_teams()
    matches = InMemoryMatches([
        Match(
            id="m1",
            tournament_id="t1",
            round_number=1,
            first_team_id="a",
            second_team_id="b",
            status=MatchStatus.COMPLETED,
            result=MatchResult.DRAW,
        ),
        Match(
            id="m2",
            tournament_id="t1",
            round_number=1,
            first_team_id="c",
            second_team_id="b",
            status=MatchStatus.COMPLETED,
            result=MatchResult.DRAW,
        ),
    ])

    standings = CalculateRoundRobinStandings(
        tournament_repository,
        teams,
        InMemoryRegistrations({"a", "b", "c"}),
        matches,
    ).execute("t1")

    assert [row.team.name for row in standings.rows] == [
        "Tigres",
        "Águias",
        "Leões",
    ]
    assert standings.rows[0].points == 2


def test_calculation_aggregates_statistics_and_applies_positive_and_negative_criteria():
    tournament_repository = InMemoryTournamentRepository()
    tournament = make_tournament()
    tournament = replace(
        tournament,
        round_robin=RoundRobinConfig(
            mode=RoundRobinMode.SINGLE,
            win_points=3,
            draw_points=1,
            loss_points=0,
            tie_breakers=(
                TieBreaker(
                    name="Gols",
                    direction=TieBreakerDirection.POSITIVE,
                ),
                TieBreaker(
                    name="Faltas",
                    direction=TieBreakerDirection.NEGATIVE,
                ),
            ),
            statistic_fields=(),
        ),
    )
    tournament_repository.add(tournament)
    teams = make_teams()
    matches = InMemoryMatches([
        Match(
            id="m1",
            tournament_id="t1",
            round_number=1,
            first_team_id="a",
            second_team_id="b",
            status=MatchStatus.COMPLETED,
            result=MatchResult.FIRST_WIN,
            first_team_stats={"Gols": 2, "Faltas": 5},
            second_team_stats={"Gols": 0, "Faltas": 2},
        ),
    ])

    standings = CalculateRoundRobinStandings(
        tournament_repository,
        teams,
        InMemoryRegistrations({"a", "b", "c"}),
        matches,
    ).execute("t1")

    assert standings.rows[0].team.id == "a"
    assert standings.rows[0].statistics["Gols"] == 2
    assert standings.rows[0].statistics["Faltas"] == 5
    assert standings.rows[1].team.id == "c"
    assert standings.rows[2].team.id == "b"


def test_finish_round_robin_rejects_pending_match():
    tournament_repository = InMemoryTournamentRepository()
    tournament_repository.add(make_tournament())
    matches = InMemoryMatches([
        Match(
            id="m1",
            tournament_id="t1",
            round_number=1,
            first_team_id="a",
            second_team_id="b",
        ),
    ])

    with pytest.raises(InvalidTournamentError, match="pendentes"):
        FinishRoundRobinTournament(
            tournament_repository,
            matches,
        ).execute("t1")


def test_finish_round_robin_sets_finished_and_exposes_leader():
    tournament_repository = InMemoryTournamentRepository()
    tournament_repository.add(make_tournament())
    matches = InMemoryMatches([
        Match(
            id="m1",
            tournament_id="t1",
            round_number=1,
            first_team_id="a",
            second_team_id="b",
            status=MatchStatus.COMPLETED,
            result=MatchResult.FIRST_WIN,
        ),
    ])

    finished = FinishRoundRobinTournament(
        tournament_repository,
        matches,
    ).execute("t1")

    assert finished.status is TournamentStatus.FINISHED
