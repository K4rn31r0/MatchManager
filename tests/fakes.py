"""Test doubles that replace infrastructure in use case tests."""

from datetime import datetime, timedelta

from server.core.entities.match import Match
from server.core.entities.team import Team
from server.core.entities.tournament import Tournament
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.registration_repository import (
    RegistrationRepository,
)
from server.core.interfaces.team_participation_query import (
    TeamParticipationQuery,
)
from server.core.interfaces.team_repository import TeamRepository
from server.core.interfaces.tournament_repository import TournamentRepository


class InMemoryTournamentRepository(TournamentRepository):
    """Fake repository that keeps tournaments in memory."""

    def __init__(self) -> None:
        self._tournaments: list[Tournament] = []

    def add(self, tournament: Tournament) -> None:
        self._tournaments.append(tournament)

    def get(self, tournament_id: str) -> Tournament | None:
        return next(
            (item for item in self._tournaments if item.id == tournament_id),
            None,
        )

    def update(self, tournament: Tournament) -> None:
        self._tournaments = [
            tournament if item.id == tournament.id else item
            for item in self._tournaments
        ]

    def delete(self, tournament_id: str) -> None:
        self._tournaments = [
            item for item in self._tournaments if item.id != tournament_id
        ]

    def participant_counts(self) -> dict[str, int]:
        return {}

    def list_all(self) -> list[Tournament]:
        return list(self._tournaments)


class SequentialIdGenerator:
    """Deterministic id generator: returns "t1", "t2", ..."""

    def __init__(self, prefix: str = "t") -> None:
        self._prefix = prefix
        self._count = 0

    def __call__(self) -> str:
        self._count += 1
        return f"{self._prefix}{self._count}"


class FakeClock:
    """Deterministic clock that advances one minute on every call."""

    def __init__(self, start: datetime = datetime(2026, 1, 1, 12, 0)) -> None:
        self._next = start

    def __call__(self) -> datetime:
        moment = self._next
        self._next += timedelta(minutes=1)
        return moment


class InMemoryTeamRepository(TeamRepository):
    """Fake repository that keeps teams in memory, keyed by id."""

    def __init__(self) -> None:
        self._teams: dict[str, Team] = {}

    def add(self, team: Team) -> None:
        self._teams[team.id] = team

    def get(self, team_id: str) -> Team | None:
        return self._teams.get(team_id)

    def update(self, team: Team) -> None:
        self._teams[team.id] = team

    def delete(self, team_id: str) -> None:
        del self._teams[team_id]

    def list_all(self) -> list[Team]:
        return list(self._teams.values())


class InMemoryMatchRepository(MatchRepository):
    """Fake match repository keyed by match id."""

    def __init__(self) -> None:
        self._matches: dict[str, Match] = {}

    def replace_for_tournament(
        self, tournament_id: str, matches: list[Match],
    ) -> None:
        self._matches = {
            match_id: match
            for match_id, match in self._matches.items()
            if match.tournament_id != tournament_id
        }
        for match in matches:
            self._matches[match.id] = match

    def get(self, match_id: str) -> Match | None:
        return self._matches.get(match_id)

    def list_for_tournament(self, tournament_id: str) -> list[Match]:
        return [
            match for match in self._matches.values()
            if match.tournament_id == tournament_id
        ]

    def update(self, match: Match) -> None:
        self._matches[match.id] = match


class InMemoryRegistrationRepository(RegistrationRepository):
    """Fake registration repository that stores new teams in a team fake."""

    def __init__(self, teams: TeamRepository) -> None:
        self._teams = teams
        self._team_ids: dict[str, set[str]] = {}

    def team_ids(self, tournament_id: str) -> set[str]:
        return set(self._team_ids.get(tournament_id, set()))

    def add(self, tournament_id: str, team_id: str) -> None:
        self._team_ids.setdefault(tournament_id, set()).add(team_id)

    def add_new_team(self, tournament_id: str, team: Team) -> None:
        self._teams.add(team)
        self.add(tournament_id, team.id)

    def remove(self, tournament_id: str, team_id: str) -> None:
        self._team_ids.get(tournament_id, set()).discard(team_id)


class FakeTeamParticipationQuery(TeamParticipationQuery):
    """Answers from a fixed set of teams that play started tournaments."""

    def __init__(self, teams_in_started_tournaments: set[str] = frozenset()):
        self._team_ids = set(teams_in_started_tournaments)

    def is_in_started_tournament(self, team_id: str) -> bool:
        return team_id in self._team_ids
