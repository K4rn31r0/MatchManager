"""Value objects and bracket construction rules for knockout tournaments."""

from collections.abc import Callable
from dataclasses import dataclass

from server.core.entities.match import Match


@dataclass(frozen=True)
class KnockoutRound:
    number: int
    matches: tuple[Match, ...]
    bye_team_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class KnockoutBracket:
    rounds: tuple[KnockoutRound, ...]
    champion_team_id: str | None = None


def bracket_size(team_count: int) -> int:
    return 1 << (team_count - 1).bit_length()

def knockout_round_count(team_count: int) -> int:
    return bracket_size(team_count).bit_length() - 1


def build_knockout_bracket(
    tournament_id: str,
    initial_order: list[str],
    bye_team_ids: list[str],
    id_generator: Callable[[], str],
) -> KnockoutBracket:
    bye_set = set(bye_team_ids)
    seeded_teams = [
        *[team_id for team_id in initial_order if team_id in bye_set],
        *[team_id for team_id in initial_order if team_id not in bye_set],
    ]
    size = bracket_size(len(seeded_teams))
    slots: list[str | None] = [None] * size
    for position, seed in enumerate(_seed_positions(size), start=1):
        if seed <= len(seeded_teams):
            slots[position - 1] = seeded_teams[seed - 1]

    first_round: list[Match] = []
    first_round_byes: list[str] = []
    outcomes: list[str | None] = []
    for offset in range(0, size, 2):
        first_team_id, second_team_id = slots[offset:offset + 2]
        if first_team_id is not None and second_team_id is not None:
            first_round.append(
                Match(
                    id=id_generator(),
                    tournament_id=tournament_id,
                    round_number=1,
                    bracket_position=offset // 2 + 1,
                    first_team_id=first_team_id,
                    second_team_id=second_team_id,
                )
            )
            outcomes.append(None)
        else:
            bye_team_id = (
                first_team_id
                if first_team_id is not None
                else second_team_id
            )
            if bye_team_id is not None:
                first_round_byes.append(bye_team_id)
            outcomes.append(bye_team_id)

    rounds = [
        KnockoutRound(
            number=1,
            matches=tuple(first_round),
            bye_team_ids=tuple(first_round_byes),
        )
    ]
    round_number = 2
    while len(outcomes) > 1:
        next_round: list[Match] = []
        next_outcomes: list[str | None] = []
        for offset in range(0, len(outcomes), 2):
            next_round.append(
                Match(
                    id=id_generator(),
                    tournament_id=tournament_id,
                    round_number=round_number,
                    bracket_position=offset // 2 + 1,
                    first_team_id=outcomes[offset],
                    second_team_id=outcomes[offset + 1],
                )
            )
            next_outcomes.append(None)
        rounds.append(
            KnockoutRound(number=round_number, matches=tuple(next_round))
        )
        outcomes = next_outcomes
        round_number += 1
    return KnockoutBracket(rounds=tuple(rounds))


def _seed_positions(size: int) -> list[int]:
    positions = [1, 2]
    while len(positions) < size:
        next_size = len(positions) * 2
        positions = [
            position
            for seed in positions
            for position in (seed, next_size + 1 - seed)
        ]
    return positions
