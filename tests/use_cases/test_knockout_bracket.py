from datetime import datetime

import pytest

from server.core.entities.tournament import Tournament, TournamentFormat
from server.core.errors import InvalidTournamentError
from server.core.use_cases.generate_knockout_bracket import (
    GenerateKnockoutBracket,
    KnockoutBracketInput,
)
from server.core.use_cases.start_knockout_tournament import (
    StartKnockoutTournament,
)
from server.core.entities.tournament import (
    KnockoutByeStrategy,
    KnockoutOrderMode,
)
from tests.fakes import InMemoryTournamentRepository


class InMemoryRegistrations:
    def __init__(self, team_ids):
        self._team_ids = set(team_ids)

    def team_ids(self, tournament_id):
        return set(self._team_ids)


class InMemoryMatches:
    def __init__(self):
        self.items = []

    def replace_for_tournament(self, tournament_id, matches):
        self.items = list(matches)

    def list_for_tournament(self, tournament_id):
        return list(self.items)

    def get(self, match_id):
        return next((item for item in self.items if item.id == match_id), None)

    def update(self, match):
        self.items = [
            match if item.id == match.id else item for item in self.items
        ]


def test_generated_bracket_keeps_order_and_advances_byes():
    tournaments = InMemoryTournamentRepository()
    tournament = Tournament.create_draft(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1),
    )
    tournaments.add(tournament)
    matches = InMemoryMatches()
    ids = iter(f"match-{number}" for number in range(1, 10))
    use_case = GenerateKnockoutBracket(
        tournaments,
        InMemoryRegistrations({"a", "b", "c", "d", "e"}),
        matches,
        id_generator=lambda: next(ids),
    )

    bracket = use_case.execute(
        "cup",
        KnockoutBracketInput(
            order_mode=KnockoutOrderMode.MANUAL,
            initial_order=("e", "d", "c", "b", "a"),
            bye_strategy=KnockoutByeStrategy.PERFORMANCE,
        ),
    )

    assert [round_data.number for round_data in bracket.rounds] == [1, 2, 3]
    assert bracket.rounds[0].bye_team_ids == ("e", "d", "c")
    assert len(bracket.rounds[0].matches) == 1
    assert (
        bracket.rounds[0].matches[0].first_team_id,
        bracket.rounds[0].matches[0].second_team_id,
    ) == ("b", "a")
    assert [
        (match.first_team_id, match.second_team_id)
        for match in bracket.rounds[1].matches
    ] == [("e", None), ("d", "c")]
    assert len(bracket.rounds[2].matches) == 1
    assert (
        bracket.rounds[2].matches[0].first_team_id,
        bracket.rounds[2].matches[0].second_team_id,
    ) == (None, None)
    assert sum(len(round_data.matches) for round_data in bracket.rounds) == 4
    assert len(matches.items) == 4
    assert tournaments.get("cup").knockout.initial_order == (
        "e", "d", "c", "b", "a",
    )


def test_draw_order_and_draw_strategy_use_the_randomized_order_for_byes():
    tournaments = InMemoryTournamentRepository()
    tournament = Tournament.create_draft(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1),
    )
    tournaments.add(tournament)
    matches = InMemoryMatches()
    use_case = GenerateKnockoutBracket(
        tournaments,
        InMemoryRegistrations({"a", "b", "c", "d", "e"}),
        matches,
        id_generator=iter(f"m{n}" for n in range(1, 10)).__next__,
        shuffle=lambda teams: teams.reverse(),
        sample=lambda teams, count: ["b", "d", "e"][:count],
    )

    bracket = use_case.execute(
        "cup",
        KnockoutBracketInput(
            order_mode=KnockoutOrderMode.DRAW,
            bye_strategy=KnockoutByeStrategy.DRAW,
        ),
    )

    config = tournaments.get("cup").knockout
    assert config.initial_order == ("e", "d", "c", "b", "a")
    assert config.bye_team_ids == ("e", "d", "b")
    assert bracket.rounds[0].bye_team_ids == ("e", "d", "b")


def test_manual_bye_strategy_uses_only_the_selected_teams():
    tournaments = InMemoryTournamentRepository()
    tournament = Tournament.create_draft(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1),
    )
    tournaments.add(tournament)
    use_case = GenerateKnockoutBracket(
        tournaments,
        InMemoryRegistrations({"a", "b", "c", "d", "e"}),
        InMemoryMatches(),
        id_generator=iter(f"m{n}" for n in range(1, 10)).__next__,
    )

    bracket = use_case.execute(
        "cup",
        KnockoutBracketInput(
            order_mode=KnockoutOrderMode.MANUAL,
            initial_order=("a", "b", "c", "d", "e"),
            bye_strategy=KnockoutByeStrategy.MANUAL,
            bye_team_ids=("e", "c", "a"),
        ),
    )

    assert bracket.rounds[0].bye_team_ids == ("a", "c", "e")
    assert len(bracket.rounds[0].matches) == 1


@pytest.mark.parametrize("team_count", [2, 3, 4, 5, 6, 8, 9])
def test_generated_bracket_has_valid_rounds_and_one_match_per_elimination(
    team_count,
):
    tournaments = InMemoryTournamentRepository()
    tournaments.add(Tournament.create_draft(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1),
    ))
    team_ids = tuple(f"team-{number}" for number in range(team_count))
    matches = InMemoryMatches()
    bracket = GenerateKnockoutBracket(
        tournaments,
        InMemoryRegistrations(team_ids),
        matches,
        id_generator=iter(
            f"match-{number}" for number in range(1, team_count + 1)
        ).__next__,
    ).execute(
        "cup",
        KnockoutBracketInput(
            order_mode=KnockoutOrderMode.MANUAL,
            initial_order=team_ids,
            bye_strategy=KnockoutByeStrategy.PERFORMANCE,
        ),
    )

    size = 1 << (team_count - 1).bit_length()
    assert len(bracket.rounds) == size.bit_length() - 1
    assert sum(len(round_data.matches) for round_data in bracket.rounds) == (
        team_count - 1
    )
    assert len(bracket.rounds[0].bye_team_ids) == size - team_count
    assert all(
        match.first_team_id is not None and match.second_team_id is not None
        for match in bracket.rounds[0].matches
    )
    assert bracket.rounds[-1].number == len(bracket.rounds)


def test_start_rejects_tournament_without_a_valid_knockout_bracket():
    tournaments = InMemoryTournamentRepository()
    tournament = Tournament.create_draft(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1),
    )
    tournaments.add(tournament)
    registrations = InMemoryRegistrations({"a", "b"})

    with pytest.raises(InvalidTournamentError, match="chaveamento"):
        StartKnockoutTournament(
            tournaments, registrations, InMemoryMatches(),
        ).execute("cup")

    assert tournaments.get("cup").status.value == "draft"


def test_start_accepts_a_generated_bracket_and_changes_tournament_status():
    tournaments = InMemoryTournamentRepository()
    tournament = Tournament.create_draft(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1),
    )
    tournaments.add(tournament)
    registrations = InMemoryRegistrations({"a", "b", "c"})
    matches = InMemoryMatches()
    GenerateKnockoutBracket(
        tournaments,
        registrations,
        matches,
        id_generator=iter(f"m{n}" for n in range(1, 10)).__next__,
    ).execute(
        "cup",
        KnockoutBracketInput(
            order_mode=KnockoutOrderMode.MANUAL,
            initial_order=("a", "b", "c"),
        ),
    )

    started = StartKnockoutTournament(
        tournaments, registrations, matches,
    ).execute("cup")

    assert started.status.value == "in_progress"
    assert tournaments.get("cup").status.value == "in_progress"


def test_start_rejects_a_bracket_that_no_longer_matches_registrations():
    tournaments = InMemoryTournamentRepository()
    tournament = Tournament.create_draft(
        id="cup",
        name="Copa",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1),
    )
    tournaments.add(tournament)
    registrations = InMemoryRegistrations({"a", "b", "c"})
    matches = InMemoryMatches()
    GenerateKnockoutBracket(
        tournaments,
        registrations,
        matches,
        id_generator=iter(f"m{n}" for n in range(1, 10)).__next__,
    ).execute(
        "cup",
        KnockoutBracketInput(
            order_mode=KnockoutOrderMode.MANUAL,
            initial_order=("a", "b", "c"),
        ),
    )
    registrations._team_ids.add("d")

    with pytest.raises(InvalidTournamentError, match="chaveamento"):
        StartKnockoutTournament(
            tournaments, registrations, matches,
        ).execute("cup")

    assert tournaments.get("cup").status.value == "draft"
