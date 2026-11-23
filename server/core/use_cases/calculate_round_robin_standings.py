"""Calculate the round-robin classification."""

from dataclasses import dataclass
from functools import cmp_to_key

from server.core.entities.match import MatchResult, MatchStatus
from server.core.entities.names import normalize_name
from server.core.entities.team import Team
from server.core.entities.tournament import (
    TieBreakerDirection,
    TournamentFormat,
)
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.registration_repository import RegistrationRepository
from server.core.interfaces.team_repository import TeamRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class StandingRow:
    position: int
    team: Team
    played: int
    wins: int
    draws: int
    losses: int
    points: int
    statistics: dict[str, int | None]


@dataclass(frozen=True)
class RoundRobinStandings:
    rows: tuple[StandingRow, ...]
    champion_team_id: str | None = None
    alphabetical_fallback_applied: bool = False


class CalculateRoundRobinStandings:
    def __init__(
        self,
        tournament_repository: TournamentRepository,
        teams: TeamRepository,
        registrations: RegistrationRepository,
        matches: MatchRepository,
    ) -> None:
        self._get = GetTournament(tournament_repository)
        self._teams = teams
        self._registrations = registrations
        self._matches = matches

    def execute(self, tournament_id: str) -> RoundRobinStandings:
        tournament = self._get.execute(tournament_id)
        if tournament.tournament_format is not TournamentFormat.ROUND_ROBIN:
            raise InvalidTournamentError(
                "A classificação só existe para pontos corridos."
            )
        if tournament.round_robin is None:
            raise InvalidTournamentError(
                "Configure os pontos corridos antes de calcular a classificação."
            )
        team_ids = self._registrations.team_ids(tournament_id)
        teams = {
            team.id: team
            for team in self._teams.list_all()
            if team.id in team_ids
        }
        rows = [
            _empty_row(team)
            for team in teams.values()
        ]
        row_by_team = {row.team.id: row for row in rows}
        mutable = {
            row.team.id: {
                "team": row.team,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "points": 0,
                "statistics": {},
            }
            for row in rows
        }
        config = tournament.round_robin
        for match in self._matches.list_for_tournament(tournament_id):
            if match.status is not MatchStatus.COMPLETED:
                continue
            if match.result is None:
                continue
            first = mutable.get(match.first_team_id)
            second = mutable.get(match.second_team_id)
            if first is None or second is None:
                continue
            first["played"] += 1
            second["played"] += 1
            if match.result is MatchResult.FIRST_WIN:
                first["wins"] += 1
                second["losses"] += 1
                first["points"] += config.win_points
                second["points"] += config.loss_points
            elif match.result is MatchResult.SECOND_WIN:
                second["wins"] += 1
                first["losses"] += 1
                second["points"] += config.win_points
                first["points"] += config.loss_points
            else:
                first["draws"] += 1
                second["draws"] += 1
                first["points"] += config.draw_points
                second["points"] += config.draw_points
            _aggregate_stats(first["statistics"], match.first_team_stats)
            _aggregate_stats(second["statistics"], match.second_team_stats)

        final_rows = [
            StandingRow(
                position=0,
                team=data["team"],
                played=data["played"],
                wins=data["wins"],
                draws=data["draws"],
                losses=data["losses"],
                points=data["points"],
                statistics=data["statistics"],
            )
            for data in mutable.values()
        ]

        def compare(left: StandingRow, right: StandingRow) -> int:
            if left.points != right.points:
                return -1 if left.points > right.points else 1
            for tie_breaker in config.tie_breakers:
                left_value = left.statistics.get(tie_breaker.name)
                right_value = right.statistics.get(tie_breaker.name)
                if left_value is not None and right_value is not None:
                    if left_value != right_value:
                        if tie_breaker.direction is TieBreakerDirection.POSITIVE:
                            return -1 if left_value > right_value else 1
                        return -1 if left_value < right_value else 1
            left_name = normalize_name(left.team.name)
            right_name = normalize_name(right.team.name)
            if left_name == right_name:
                return 0
            return -1 if left_name < right_name else 1

        ordered = sorted(final_rows, key=cmp_to_key(compare))
        positioned = tuple(
            StandingRow(
                position=index,
                team=row.team,
                played=row.played,
                wins=row.wins,
                draws=row.draws,
                losses=row.losses,
                points=row.points,
                statistics=row.statistics,
            )
            for index, row in enumerate(ordered, start=1)
        )
        alphabetical_fallback_applied = any(
            left.points == right.points
            and all(
                left.statistics.get(tie_breaker.name)
                == right.statistics.get(tie_breaker.name)
                for tie_breaker in config.tie_breakers
            )
            for left, right in zip(positioned, positioned[1:])
        )
        champion = positioned[0].team.id if tournament.status.value == "finished" else None
        return RoundRobinStandings(
            rows=positioned,
            champion_team_id=champion,
            alphabetical_fallback_applied=alphabetical_fallback_applied,
        )


def _empty_row(team: Team) -> StandingRow:
    return StandingRow(
        position=0,
        team=team,
        played=0,
        wins=0,
        draws=0,
        losses=0,
        points=0,
        statistics={},
    )


def _aggregate_stats(
    aggregate: dict[str, int],
    values: dict[str, int] | None,
) -> None:
    for name, value in (values or {}).items():
        aggregate[name] = aggregate.get(name, 0) + value
