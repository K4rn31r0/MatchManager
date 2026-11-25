"""Tournament lifecycle: start, locks, corrections and finishing (issue 09).

Every use case runs against in-memory fakes, without Flask or HTTP.
"""

from dataclasses import dataclass

import pytest

from server.core.entities.match import Match, MatchResult, MatchStatus
from server.core.entities.tournament import (
    KnockoutByeStrategy,
    KnockoutOrderMode,
    RoundRobinMode,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import DomainError, InvalidTournamentError
from server.core.use_cases.calculate_round_robin_standings import (
    CalculateRoundRobinStandings,
)
from server.core.use_cases.configure_round_robin import (
    ConfigureRoundRobin,
    RoundRobinConfigInput,
)
from server.core.use_cases.create_team import CreateTeam
from server.core.use_cases.create_tournament import (
    CreateTournament,
    CreateTournamentInput,
)
from server.core.use_cases.finish_knockout_tournament import (
    FinishKnockoutTournament,
)
from server.core.use_cases.finish_round_robin_tournament import (
    FinishRoundRobinTournament,
)
from server.core.use_cases.generate_knockout_bracket import (
    GenerateKnockoutBracket,
    KnockoutBracketInput,
)
from server.core.use_cases.generate_round_robin_calendar import (
    GenerateRoundRobinCalendar,
)
from server.core.use_cases.get_knockout_bracket import GetKnockoutBracket
from server.core.use_cases.get_team import GetTeam
from server.core.use_cases.get_tournament import GetTournament
from server.core.use_cases.list_teams import ListTeams
from server.core.use_cases.record_knockout_result import (
    KnockoutResultInput,
    RecordKnockoutResult,
)
from server.core.use_cases.record_round_robin_result import (
    RecordRoundRobinResult,
    RoundRobinResultInput,
)
from server.core.use_cases.start_knockout_tournament import (
    StartKnockoutTournament,
)
from server.core.use_cases.start_round_robin_tournament import (
    StartRoundRobinTournament,
)
from server.core.use_cases.start_tournament import StartTournament
from server.core.use_cases.team_data import TeamData
from server.core.use_cases.tournament_registrations import (
    TournamentRegistrations,
)
from server.core.use_cases.update_tournament import UpdateTournament
from tests.fakes import (
    FakeClock,
    InMemoryMatchRepository,
    InMemoryRegistrationRepository,
    InMemoryTeamRepository,
    InMemoryTournamentRepository,
    SequentialIdGenerator,
)


@dataclass
class Lifecycle:
    """All lifecycle use cases wired to the same in-memory fakes."""

    tournaments: InMemoryTournamentRepository
    matches: InMemoryMatchRepository
    registrations: TournamentRegistrations
    create_tournament: CreateTournament
    create_team: CreateTeam
    update_tournament: UpdateTournament
    configure_round_robin: ConfigureRoundRobin
    generate_round_robin_calendar: GenerateRoundRobinCalendar
    generate_knockout_bracket: GenerateKnockoutBracket
    start: StartTournament
    record_round_robin_result: RecordRoundRobinResult
    record_knockout_result: RecordKnockoutResult
    standings: CalculateRoundRobinStandings
    get_knockout_bracket: GetKnockoutBracket
    finish_round_robin: FinishRoundRobinTournament
    finish_knockout: FinishKnockoutTournament

    def new_tournament(self, tournament_format: TournamentFormat) -> str:
        return self.create_tournament.execute(
            CreateTournamentInput(
                name=f"Torneio {tournament_format.value}",
                tournament_format=tournament_format,
            )
        ).id

    def register(self, tournament_id: str, *names: str) -> list[str]:
        team_ids = []
        for name in names:
            team = self.create_team.execute(TeamData(name=name))
            self.registrations.add(tournament_id, team.id)
            team_ids.append(team.id)
        return team_ids

    def configure_default_round_robin(self, tournament_id: str) -> None:
        self.configure_round_robin.execute(
            tournament_id,
            RoundRobinConfigInput(
                mode=RoundRobinMode.SINGLE,
                tie_breakers=(("Gols", "positive"),),
                statistic_fields=("Gols",),
            ),
        )

    def generate_manual_bracket(
        self, tournament_id: str, team_ids: list[str],
    ) -> None:
        self.generate_knockout_bracket.execute(
            tournament_id,
            KnockoutBracketInput(
                order_mode=KnockoutOrderMode.MANUAL,
                initial_order=tuple(team_ids),
                bye_strategy=KnockoutByeStrategy.PERFORMANCE,
            ),
        )

    def status(self, tournament_id: str) -> TournamentStatus:
        return self.tournaments.get(tournament_id).status

    def match_between(
        self, tournament_id: str, first_id: str, second_id: str,
    ) -> Match:
        return next(
            match for match in self.matches.list_for_tournament(tournament_id)
            if {match.first_team_id, match.second_team_id}
            == {first_id, second_id}
        )

    def knockout_match(
        self, tournament_id: str, round_number: int, position: int,
    ) -> Match:
        return next(
            match for match in self.matches.list_for_tournament(tournament_id)
            if match.round_number == round_number
            and match.bracket_position == position
        )

    def record_first_win(self, tournament_id: str, match: Match) -> None:
        self.record_round_robin_result.execute(
            tournament_id,
            match.id,
            RoundRobinResultInput(result=MatchResult.FIRST_WIN),
        )

    def play_knockout(
        self, tournament_id: str, match: Match, result: MatchResult,
    ) -> None:
        self.record_knockout_result.execute(
            tournament_id, match.id, KnockoutResultInput(result=result),
        )


@pytest.fixture
def lifecycle() -> Lifecycle:
    tournaments = InMemoryTournamentRepository()
    teams = InMemoryTeamRepository()
    registrations_repository = InMemoryRegistrationRepository(teams)
    matches = InMemoryMatchRepository()
    clock = FakeClock()
    create_team = CreateTeam(teams, SequentialIdGenerator("team"))
    generate_calendar = GenerateRoundRobinCalendar(
        tournaments, registrations_repository, matches,
    )
    return Lifecycle(
        tournaments=tournaments,
        matches=matches,
        registrations=TournamentRegistrations(
            registrations_repository,
            GetTournament(tournaments),
            GetTeam(teams),
            ListTeams(teams),
            create_team,
        ),
        create_tournament=CreateTournament(
            tournaments, SequentialIdGenerator(), clock,
        ),
        create_team=create_team,
        update_tournament=UpdateTournament(tournaments, clock),
        configure_round_robin=ConfigureRoundRobin(tournaments, clock),
        generate_round_robin_calendar=generate_calendar,
        generate_knockout_bracket=GenerateKnockoutBracket(
            tournaments,
            registrations_repository,
            matches,
            id_generator=SequentialIdGenerator("m"),
            clock=clock,
        ),
        start=StartTournament(
            tournaments,
            {
                TournamentFormat.ROUND_ROBIN: StartRoundRobinTournament(
                    tournaments, generate_calendar, clock,
                ),
                TournamentFormat.KNOCKOUT: StartKnockoutTournament(
                    tournaments, registrations_repository, matches, clock,
                ),
            },
        ),
        record_round_robin_result=RecordRoundRobinResult(tournaments, matches),
        record_knockout_result=RecordKnockoutResult(tournaments, matches),
        standings=CalculateRoundRobinStandings(
            tournaments, teams, registrations_repository, matches,
        ),
        get_knockout_bracket=GetKnockoutBracket(tournaments, matches),
        finish_round_robin=FinishRoundRobinTournament(
            tournaments, matches, clock,
        ),
        finish_knockout=FinishKnockoutTournament(tournaments, matches, clock),
    )


def started_round_robin(lifecycle: Lifecycle, *names: str):
    tournament_id = lifecycle.new_tournament(TournamentFormat.ROUND_ROBIN)
    team_ids = lifecycle.register(tournament_id, *names)
    lifecycle.configure_default_round_robin(tournament_id)
    lifecycle.start.execute(tournament_id)
    return tournament_id, team_ids


def started_knockout(lifecycle: Lifecycle, *names: str):
    tournament_id = lifecycle.new_tournament(TournamentFormat.KNOCKOUT)
    team_ids = lifecycle.register(tournament_id, *names)
    lifecycle.generate_manual_bracket(tournament_id, team_ids)
    lifecycle.start.execute(tournament_id)
    return tournament_id, team_ids


def finished_round_robin(lifecycle: Lifecycle):
    tournament_id, team_ids = started_round_robin(
        lifecycle, "Águias", "Tigres",
    )
    match = lifecycle.matches.list_for_tournament(tournament_id)[0]
    lifecycle.record_first_win(tournament_id, match)
    lifecycle.finish_round_robin.execute(tournament_id)
    return tournament_id, team_ids


def finished_knockout(lifecycle: Lifecycle):
    tournament_id, team_ids = started_knockout(lifecycle, "Águias", "Tigres")
    final = lifecycle.knockout_match(tournament_id, 1, 1)
    lifecycle.play_knockout(tournament_id, final, MatchResult.FIRST_WIN)
    lifecycle.finish_knockout.execute(tournament_id)
    return tournament_id, team_ids


# --- Starting ---------------------------------------------------------------


@pytest.mark.parametrize(
    "tournament_format",
    [TournamentFormat.ROUND_ROBIN, TournamentFormat.KNOCKOUT],
)
def test_start_tournament_requires_at_least_two_teams(
    lifecycle, tournament_format,
):
    tournament_id = lifecycle.new_tournament(tournament_format)
    lifecycle.register(tournament_id, "Águias")
    if tournament_format is TournamentFormat.ROUND_ROBIN:
        lifecycle.configure_default_round_robin(tournament_id)

    with pytest.raises(InvalidTournamentError):
        lifecycle.start.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.DRAFT
    assert lifecycle.matches.list_for_tournament(tournament_id) == []


def test_start_round_robin_requires_configuration(lifecycle):
    tournament_id = lifecycle.new_tournament(TournamentFormat.ROUND_ROBIN)
    lifecycle.register(tournament_id, "Águias", "Tigres")

    with pytest.raises(InvalidTournamentError, match="Configure"):
        lifecycle.start.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.DRAFT
    assert lifecycle.matches.list_for_tournament(tournament_id) == []


def test_start_knockout_requires_a_valid_bracket(lifecycle):
    tournament_id = lifecycle.new_tournament(TournamentFormat.KNOCKOUT)
    lifecycle.register(tournament_id, "Águias", "Tigres")

    with pytest.raises(InvalidTournamentError, match="chaveamento válido"):
        lifecycle.start.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.DRAFT


def test_start_knockout_rejects_bracket_outdated_by_new_registration(
    lifecycle,
):
    tournament_id = lifecycle.new_tournament(TournamentFormat.KNOCKOUT)
    team_ids = lifecycle.register(tournament_id, "Águias", "Tigres")
    lifecycle.generate_manual_bracket(tournament_id, team_ids)
    lifecycle.register(tournament_id, "Leões")

    with pytest.raises(InvalidTournamentError, match="chaveamento válido"):
        lifecycle.start.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.DRAFT


def test_start_round_robin_generates_every_match_and_sets_in_progress(
    lifecycle,
):
    tournament_id, _ = started_round_robin(
        lifecycle, "Águias", "Tigres", "Leões", "Lobos",
    )

    assert lifecycle.status(tournament_id) is TournamentStatus.IN_PROGRESS
    matches = lifecycle.matches.list_for_tournament(tournament_id)
    assert len(matches) == 6
    assert all(match.status is MatchStatus.PENDING for match in matches)


def test_start_round_robin_regenerates_calendar_previewed_in_draft(
    lifecycle,
):
    tournament_id = lifecycle.new_tournament(TournamentFormat.ROUND_ROBIN)
    lifecycle.register(tournament_id, "Águias", "Tigres")
    lifecycle.configure_default_round_robin(tournament_id)
    lifecycle.generate_round_robin_calendar.execute(tournament_id)
    lifecycle.register(tournament_id, "Leões")

    lifecycle.start.execute(tournament_id)

    assert len(lifecycle.matches.list_for_tournament(tournament_id)) == 3


def test_start_knockout_keeps_the_generated_bracket(lifecycle):
    tournament_id, _ = started_knockout(
        lifecycle, "Águias", "Tigres", "Leões", "Lobos",
    )

    assert lifecycle.status(tournament_id) is TournamentStatus.IN_PROGRESS
    assert len(lifecycle.matches.list_for_tournament(tournament_id)) == 3


@pytest.mark.parametrize("starter", [started_round_robin, started_knockout])
def test_start_closes_registrations(lifecycle, starter):
    tournament_id, team_ids = starter(lifecycle, "Águias", "Tigres")
    outsider = lifecycle.create_team.execute(TeamData(name="Leões"))

    with pytest.raises(InvalidTournamentError, match="inscrições"):
        lifecycle.registrations.add(tournament_id, outsider.id)
    with pytest.raises(InvalidTournamentError, match="inscrições"):
        lifecycle.registrations.create_and_add(
            tournament_id, TeamData(name="Lobos"),
        )
    with pytest.raises(InvalidTournamentError, match="inscrições"):
        lifecycle.registrations.remove(tournament_id, team_ids[0])


@pytest.mark.parametrize("starter", [started_round_robin, started_knockout])
def test_started_tournament_cannot_be_started_again(lifecycle, starter):
    tournament_id, _ = starter(lifecycle, "Águias", "Tigres")
    matches_before = lifecycle.matches.list_for_tournament(tournament_id)

    with pytest.raises(InvalidTournamentError, match="rascunho"):
        lifecycle.start.execute(tournament_id)

    assert lifecycle.matches.list_for_tournament(tournament_id) == (
        matches_before
    )


def test_start_tournament_rejects_format_without_starter(lifecycle):
    tournament_id = lifecycle.new_tournament(TournamentFormat.KNOCKOUT)
    use_case = StartTournament(lifecycle.tournaments, {})

    with pytest.raises(InvalidTournamentError, match="formato"):
        use_case.execute(tournament_id)


# --- Configuration lock -----------------------------------------------------


@pytest.mark.parametrize(
    "prepare", [started_round_robin, lambda lc, *_: finished_round_robin(lc)],
    ids=["in_progress", "finished"],
)
def test_round_robin_configuration_is_locked_after_start(lifecycle, prepare):
    tournament_id, _ = prepare(lifecycle, "Águias", "Tigres")
    tournament = lifecycle.tournaments.get(tournament_id)
    config_before = tournament.round_robin
    matches_before = lifecycle.matches.list_for_tournament(tournament_id)

    with pytest.raises(InvalidTournamentError, match="rascunho"):
        lifecycle.configure_round_robin.execute(
            tournament_id,
            RoundRobinConfigInput(
                mode=RoundRobinMode.DOUBLE,
                win_points=2,
                tie_breakers=(("Faltas", "negative"),),
                statistic_fields=("Faltas",),
            ),
        )
    with pytest.raises(InvalidTournamentError, match="rascunho"):
        lifecycle.generate_round_robin_calendar.execute(tournament_id)
    with pytest.raises(InvalidTournamentError, match="rascunho"):
        lifecycle.update_tournament.execute(
            tournament_id,
            CreateTournamentInput(
                name="Outro nome",
                tournament_format=TournamentFormat.KNOCKOUT,
            ),
        )

    current = lifecycle.tournaments.get(tournament_id)
    assert current.round_robin == config_before
    assert current.tournament_format is TournamentFormat.ROUND_ROBIN
    assert lifecycle.matches.list_for_tournament(tournament_id) == (
        matches_before
    )


@pytest.mark.parametrize(
    "prepare", [started_knockout, lambda lc, *_: finished_knockout(lc)],
    ids=["in_progress", "finished"],
)
def test_knockout_structure_is_locked_after_start(lifecycle, prepare):
    tournament_id, team_ids = prepare(lifecycle, "Águias", "Tigres")
    config_before = lifecycle.tournaments.get(tournament_id).knockout

    with pytest.raises(InvalidTournamentError, match="rascunho"):
        lifecycle.generate_manual_bracket(
            tournament_id, list(reversed(team_ids)),
        )

    assert lifecycle.tournaments.get(tournament_id).knockout == config_before


@pytest.mark.parametrize(
    "finisher", [finished_round_robin, finished_knockout],
)
def test_finished_tournament_keeps_registrations_closed(lifecycle, finisher):
    tournament_id, _ = finisher(lifecycle)
    outsider = lifecycle.create_team.execute(TeamData(name="Leões"))

    with pytest.raises(InvalidTournamentError, match="inscrições"):
        lifecycle.registrations.add(tournament_id, outsider.id)
    with pytest.raises(InvalidTournamentError, match="rascunho"):
        lifecycle.start.execute(tournament_id)
    assert lifecycle.status(tournament_id) is TournamentStatus.FINISHED


# --- Results before start -----------------------------------------------


def test_round_robin_result_is_rejected_before_start(lifecycle):
    tournament_id = lifecycle.new_tournament(TournamentFormat.ROUND_ROBIN)
    lifecycle.register(tournament_id, "Águias", "Tigres")
    lifecycle.configure_default_round_robin(tournament_id)
    lifecycle.generate_round_robin_calendar.execute(tournament_id)
    match = lifecycle.matches.list_for_tournament(tournament_id)[0]

    with pytest.raises(InvalidTournamentError, match="iniciados"):
        lifecycle.record_first_win(tournament_id, match)


def test_knockout_result_is_rejected_before_start(lifecycle):
    tournament_id = lifecycle.new_tournament(TournamentFormat.KNOCKOUT)
    team_ids = lifecycle.register(tournament_id, "Águias", "Tigres")
    lifecycle.generate_manual_bracket(tournament_id, team_ids)
    match = lifecycle.knockout_match(tournament_id, 1, 1)

    with pytest.raises(InvalidTournamentError, match="iniciados"):
        lifecycle.play_knockout(tournament_id, match, MatchResult.FIRST_WIN)


# --- Round-robin corrections ------------------------------------------------


def test_round_robin_correction_in_progress_recalculates_standings(lifecycle):
    tournament_id, (eagles, tigers) = started_round_robin(
        lifecycle, "Águias", "Tigres",
    )
    match = lifecycle.match_between(tournament_id, eagles, tigers)
    lifecycle.record_round_robin_result.execute(
        tournament_id,
        match.id,
        RoundRobinResultInput(
            result=MatchResult.FIRST_WIN,
            first_score=2,
            second_score=0,
            first_team_stats={"Gols": 2},
            second_team_stats={"Gols": 0},
        ),
    )
    winner_id = match.first_team_id

    lifecycle.record_round_robin_result.execute(
        tournament_id,
        match.id,
        RoundRobinResultInput(
            result=MatchResult.DRAW,
            first_score=1,
            second_score=1,
            first_team_stats={"Gols": 1},
            second_team_stats={"Gols": 1},
        ),
    )

    rows = {
        row.team.id: row
        for row in lifecycle.standings.execute(tournament_id).rows
    }
    assert rows[winner_id].wins == 0
    assert rows[winner_id].draws == 1
    assert rows[winner_id].points == 1
    assert rows[winner_id].statistics == {"Gols": 1}
    assert lifecycle.status(tournament_id) is TournamentStatus.IN_PROGRESS


def test_round_robin_correction_after_finish_keeps_status_and_updates_champion(
    lifecycle,
):
    tournament_id, _ = finished_round_robin(lifecycle)
    match = lifecycle.matches.list_for_tournament(tournament_id)[0]
    assert (
        lifecycle.standings.execute(tournament_id).champion_team_id
        == match.first_team_id
    )

    lifecycle.record_round_robin_result.execute(
        tournament_id,
        match.id,
        RoundRobinResultInput(result=MatchResult.SECOND_WIN),
    )

    assert lifecycle.status(tournament_id) is TournamentStatus.FINISHED
    standings = lifecycle.standings.execute(tournament_id)
    assert standings.champion_team_id == match.second_team_id
    assert standings.rows[0].points == 3


def test_invalid_round_robin_correction_keeps_previous_result(lifecycle):
    tournament_id, _ = finished_round_robin(lifecycle)
    match = lifecycle.matches.list_for_tournament(tournament_id)[0]

    with pytest.raises(InvalidTournamentError, match="placar completo"):
        lifecycle.record_round_robin_result.execute(
            tournament_id,
            match.id,
            RoundRobinResultInput(
                result=MatchResult.SECOND_WIN, first_score=1,
            ),
        )

    assert lifecycle.matches.get(match.id).result is MatchResult.FIRST_WIN
    assert lifecycle.status(tournament_id) is TournamentStatus.FINISHED


# --- Knockout corrections ---------------------------------------------------


def test_knockout_correction_allowed_while_dependent_match_is_pending(
    lifecycle,
):
    names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    tournament_id, _ = started_knockout(lifecycle, *names)
    for position in range(1, 5):
        lifecycle.play_knockout(
            tournament_id,
            lifecycle.knockout_match(tournament_id, 1, position),
            MatchResult.FIRST_WIN,
        )
    lifecycle.play_knockout(
        tournament_id,
        lifecycle.knockout_match(tournament_id, 2, 2),
        MatchResult.FIRST_WIN,
    )
    quarter_final = lifecycle.knockout_match(tournament_id, 1, 1)

    lifecycle.play_knockout(
        tournament_id, quarter_final, MatchResult.SECOND_WIN,
    )

    semi_final = lifecycle.knockout_match(tournament_id, 2, 1)
    assert semi_final.first_team_id == quarter_final.second_team_id
    assert (
        lifecycle.knockout_match(tournament_id, 1, 1).result
        is MatchResult.SECOND_WIN
    )


def test_knockout_correction_blocked_after_dependent_match_occurred(
    lifecycle,
):
    tournament_id, _ = started_knockout(lifecycle, "A", "B", "C", "D")
    for position in (1, 2):
        lifecycle.play_knockout(
            tournament_id,
            lifecycle.knockout_match(tournament_id, 1, position),
            MatchResult.FIRST_WIN,
        )
    lifecycle.play_knockout(
        tournament_id,
        lifecycle.knockout_match(tournament_id, 2, 1),
        MatchResult.FIRST_WIN,
    )
    final_before = lifecycle.knockout_match(tournament_id, 2, 1)

    with pytest.raises(InvalidTournamentError, match="partida subsequente"):
        lifecycle.play_knockout(
            tournament_id,
            lifecycle.knockout_match(tournament_id, 1, 1),
            MatchResult.SECOND_WIN,
        )

    assert (
        lifecycle.knockout_match(tournament_id, 1, 1).result
        is MatchResult.FIRST_WIN
    )
    assert lifecycle.knockout_match(tournament_id, 2, 1) == final_before


def test_knockout_final_correction_after_finish_keeps_status(lifecycle):
    tournament_id, _ = finished_knockout(lifecycle)
    final = lifecycle.knockout_match(tournament_id, 1, 1)

    lifecycle.play_knockout(tournament_id, final, MatchResult.SECOND_WIN)

    assert lifecycle.status(tournament_id) is TournamentStatus.FINISHED
    bracket = lifecycle.get_knockout_bracket.execute(tournament_id)
    assert bracket.champion_team_id == final.second_team_id


def test_knockout_correction_after_finish_blocked_before_the_final(
    lifecycle,
):
    tournament_id, _ = started_knockout(lifecycle, "A", "B", "C", "D")
    for position in (1, 2):
        lifecycle.play_knockout(
            tournament_id,
            lifecycle.knockout_match(tournament_id, 1, position),
            MatchResult.FIRST_WIN,
        )
    lifecycle.play_knockout(
        tournament_id,
        lifecycle.knockout_match(tournament_id, 2, 1),
        MatchResult.SECOND_WIN,
    )
    lifecycle.finish_knockout.execute(tournament_id)

    with pytest.raises(InvalidTournamentError, match="partida subsequente"):
        lifecycle.play_knockout(
            tournament_id,
            lifecycle.knockout_match(tournament_id, 1, 2),
            MatchResult.SECOND_WIN,
        )

    assert lifecycle.status(tournament_id) is TournamentStatus.FINISHED


# --- Finishing --------------------------------------------------------------


def test_round_robin_finish_blocked_while_a_match_is_pending(lifecycle):
    tournament_id, _ = started_round_robin(
        lifecycle, "Águias", "Tigres", "Leões",
    )
    matches = lifecycle.matches.list_for_tournament(tournament_id)
    for match in matches[:-1]:
        lifecycle.record_first_win(tournament_id, match)

    with pytest.raises(InvalidTournamentError, match="pendentes"):
        lifecycle.finish_round_robin.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.IN_PROGRESS
    assert lifecycle.standings.execute(tournament_id).champion_team_id is None

    lifecycle.record_first_win(tournament_id, matches[-1])
    lifecycle.finish_round_robin.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.FINISHED


def test_knockout_finish_blocked_while_the_final_is_pending(lifecycle):
    tournament_id, _ = started_knockout(lifecycle, "A", "B", "C")
    lifecycle.play_knockout(
        tournament_id,
        lifecycle.knockout_match(tournament_id, 1, 2),
        MatchResult.FIRST_WIN,
    )

    with pytest.raises(InvalidTournamentError, match="pendentes"):
        lifecycle.finish_knockout.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.IN_PROGRESS


def test_draft_tournament_cannot_be_finished(lifecycle):
    tournament_id = lifecycle.new_tournament(TournamentFormat.ROUND_ROBIN)
    lifecycle.register(tournament_id, "Águias", "Tigres")
    lifecycle.configure_default_round_robin(tournament_id)

    with pytest.raises(DomainError, match="em andamento"):
        lifecycle.finish_round_robin.execute(tournament_id)

    assert lifecycle.status(tournament_id) is TournamentStatus.DRAFT


@pytest.mark.parametrize(
    ("finisher", "finish_name"),
    [
        (finished_round_robin, "finish_round_robin"),
        (finished_knockout, "finish_knockout"),
    ],
)
def test_finished_tournament_cannot_be_finished_again(
    lifecycle, finisher, finish_name,
):
    tournament_id, _ = finisher(lifecycle)

    with pytest.raises(InvalidTournamentError, match="em andamento"):
        getattr(lifecycle, finish_name).execute(tournament_id)
