from dataclasses import replace

import pytest

from server.core.entities.tournament import (
    RoundRobinMode,
    TieBreakerDirection,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError
from server.core.use_cases.configure_round_robin import (
    ConfigureRoundRobin,
    RoundRobinConfigInput,
)
from server.core.use_cases.generate_round_robin_calendar import (
    GenerateRoundRobinCalendar,
)
from server.core.use_cases.create_tournament import (
    CreateTournament,
    CreateTournamentInput,
)
from tests.fakes import (
    FakeClock,
    InMemoryTournamentRepository,
    SequentialIdGenerator,
)


@pytest.fixture
def tournament(tournament_repository):
    use_case = CreateTournament(
        tournament_repository, SequentialIdGenerator(), FakeClock()
    )
    return use_case.execute(
        CreateTournamentInput(
            name="Liga",
            tournament_format=TournamentFormat.ROUND_ROBIN,
        )
    )


def test_configure_round_robin_uses_defaults_and_positive_negative_criteria(
    tournament_repository,
    tournament,
):
    use_case = ConfigureRoundRobin(tournament_repository)

    configured = use_case.execute(
        tournament.id,
        RoundRobinConfigInput(
            mode=RoundRobinMode.SINGLE,
            tie_breakers=[
                ("Saldo de gols", "positive"),
                ("Cartões", "negative"),
            ],
            statistic_fields=["Gols", "Cartões"],
        ),
    )

    assert configured.round_robin is not None
    assert configured.round_robin.mode is RoundRobinMode.SINGLE
    assert configured.round_robin.win_points == 3
    assert configured.round_robin.draw_points == 1
    assert configured.round_robin.loss_points == 0
    assert (
        configured.round_robin.tie_breakers[0].direction
        is TieBreakerDirection.POSITIVE
    )
    assert (
        configured.round_robin.tie_breakers[1].direction
        is TieBreakerDirection.NEGATIVE
    )
    assert tuple(
        field.name for field in configured.round_robin.statistic_fields
    ) == ("Gols", "Cartões")


@pytest.mark.parametrize(
    ("win_points", "draw_points", "loss_points"),
    [(2, 2, 1), (1, 2, 0), (3, 1, 2), (3, 0, 1)],
)
def test_configure_round_robin_rejects_invalid_points(
    tournament_repository,
    tournament,
    win_points,
    draw_points,
    loss_points,
):
    use_case = ConfigureRoundRobin(tournament_repository)

    with pytest.raises(
        InvalidTournamentError, match="vitória.*empate.*derrota"
    ):
        use_case.execute(
            tournament.id,
            RoundRobinConfigInput(
                mode=RoundRobinMode.DOUBLE,
                win_points=win_points,
                draw_points=draw_points,
                loss_points=loss_points,
                tie_breakers=[("Saldo", "positive")],
            ),
        )


def test_configure_round_robin_requires_a_tie_breaker(
    tournament_repository,
    tournament,
):
    use_case = ConfigureRoundRobin(tournament_repository)

    with pytest.raises(InvalidTournamentError, match="desempate"):
        use_case.execute(
            tournament.id,
            RoundRobinConfigInput(mode=RoundRobinMode.SINGLE, tie_breakers=[]),
        )


def test_configure_round_robin_is_blocked_after_start(
    tournament_repository,
    tournament,
):
    tournament_repository.update(
        replace(tournament, status=TournamentStatus.IN_PROGRESS)
    )

    with pytest.raises(InvalidTournamentError, match="rascunho"):
        ConfigureRoundRobin(tournament_repository).execute(
            tournament.id,
            RoundRobinConfigInput(
                mode=RoundRobinMode.SINGLE,
                tie_breakers=[("Saldo", "positive")],
            ),
        )


@pytest.mark.parametrize(
    ("tie_breakers", "message"),
    [
        ([("", "positive")], "nome"),
        ([("Saldo", "unknown")], "positivo ou negativo"),
    ],
)
def test_configure_round_robin_rejects_invalid_tie_breaker(
    tournament_repository,
    tournament,
    tie_breakers,
    message,
):
    with pytest.raises(InvalidTournamentError, match=message):
        ConfigureRoundRobin(tournament_repository).execute(
            tournament.id,
            RoundRobinConfigInput(
                mode=RoundRobinMode.SINGLE,
                tie_breakers=tie_breakers,
            ),
        )


class InMemoryRegistrations:
    def __init__(self, team_ids: set[str]) -> None:
        self._team_ids = team_ids

    def team_ids(self, tournament_id: str) -> set[str]:
        return set(self._team_ids)


class InMemoryMatches:
    def __init__(self) -> None:
        self.items = []

    def replace_for_tournament(self, tournament_id: str, matches) -> None:
        self.items = list(matches)


def configure_tournament(tournament_repository, tournament, mode):
    return ConfigureRoundRobin(tournament_repository).execute(
        tournament.id,
        RoundRobinConfigInput(
            mode=mode,
            tie_breakers=[("Saldo", "positive")],
        ),
    )


def test_generate_single_round_robin_has_one_match_per_pair(
    tournament_repository,
    tournament,
):
    configure_tournament(
        tournament_repository, tournament, RoundRobinMode.SINGLE
    )
    matches = InMemoryMatches()
    calendar = GenerateRoundRobinCalendar(
        tournament_repository,
        InMemoryRegistrations({"a", "b", "c", "d"}),
        matches,
    ).execute(tournament.id)

    fixtures = [
        fixture
        for round_data in calendar.rounds
        for fixture in round_data.matches
    ]
    pairs = {
        frozenset((fixture.first_team_id, fixture.second_team_id))
        for fixture in fixtures
    }
    assert len(fixtures) == 6
    assert len(pairs) == 6
    assert all(len(pair) == 2 for pair in pairs)
    assert len(matches.items) == 6


def test_generate_double_round_robin_has_both_directions(
    tournament_repository,
    tournament,
):
    configure_tournament(
        tournament_repository, tournament, RoundRobinMode.DOUBLE
    )
    calendar = GenerateRoundRobinCalendar(
        tournament_repository,
        InMemoryRegistrations({"a", "b", "c"}),
        InMemoryMatches(),
    ).execute(tournament.id)

    fixtures = [
        fixture
        for round_data in calendar.rounds
        for fixture in round_data.matches
    ]
    directed_pairs = {
        (fixture.first_team_id, fixture.second_team_id) for fixture in fixtures
    }
    assert len(fixtures) == 6
    assert ("a", "b") in directed_pairs
    assert ("b", "a") in directed_pairs


def test_generate_calendar_for_odd_teams_has_valid_rest_rounds(
    tournament_repository,
    tournament,
):
    configure_tournament(
        tournament_repository, tournament, RoundRobinMode.SINGLE
    )
    calendar = GenerateRoundRobinCalendar(
        tournament_repository,
        InMemoryRegistrations({"a", "b", "c", "d", "e"}),
        InMemoryMatches(),
    ).execute(tournament.id)

    assert len(calendar.rounds) == 5
    assert all(
        len(round_data.resting_team_ids) == 1 for round_data in calendar.rounds
    )
    assert sum(len(round_data.matches) for round_data in calendar.rounds) == 10


def test_generate_double_calendar_repeats_valid_rest_rounds(
    tournament_repository,
    tournament,
):
    configure_tournament(
        tournament_repository, tournament, RoundRobinMode.DOUBLE
    )
    calendar = GenerateRoundRobinCalendar(
        tournament_repository,
        InMemoryRegistrations({"a", "b", "c", "d", "e"}),
        InMemoryMatches(),
    ).execute(tournament.id)

    assert len(calendar.rounds) == 10
    assert all(
        len(round_data.resting_team_ids) == 1 for round_data in calendar.rounds
    )
    assert sum(len(round_data.matches) for round_data in calendar.rounds) == 20


def test_generate_calendar_requires_two_registered_teams(
    tournament_repository,
    tournament,
):
    configure_tournament(
        tournament_repository, tournament, RoundRobinMode.SINGLE
    )

    with pytest.raises(InvalidTournamentError, match="duas equipes"):
        GenerateRoundRobinCalendar(
            tournament_repository,
            InMemoryRegistrations({"a"}),
            InMemoryMatches(),
        ).execute(tournament.id)
