"""Start a round-robin tournament, generating its full calendar."""

from collections.abc import Callable
from datetime import datetime

from server.core.entities.tournament import Tournament
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.generate_round_robin_calendar import (
    GenerateRoundRobinCalendar,
)
from server.core.use_cases.get_tournament import GetTournament


class StartRoundRobinTournament:
    """Generates every match and moves the tournament to in progress.

    The tournament validates the draft status and its configuration, and
    the calendar generation validates the minimum of two registered teams,
    before anything is persisted.
    """

    def __init__(
        self,
        tournaments: TournamentRepository,
        generate_calendar: GenerateRoundRobinCalendar,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._get_tournament = GetTournament(tournaments)
        self._tournaments = tournaments
        self._generate_calendar = generate_calendar
        self._clock = clock or datetime.now

    def execute(self, tournament_id: str) -> Tournament:
        tournament = self._get_tournament.execute(tournament_id)
        started = tournament.start(self._clock())
        self._generate_calendar.execute(tournament_id)
        self._tournaments.update(started)
        return started
