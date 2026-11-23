"""Test doubles that replace infrastructure in use case tests."""

from datetime import datetime, timedelta

from server.core.entities.tournament import Tournament
from server.core.interfaces.tournament_repository import TournamentRepository


class InMemoryTournamentRepository(TournamentRepository):
    """Fake repository that keeps tournaments in memory."""

    def __init__(self) -> None:
        self._tournaments: list[Tournament] = []

    def add(self, tournament: Tournament) -> None:
        self._tournaments.append(tournament)

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
