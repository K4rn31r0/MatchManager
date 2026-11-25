"""Set the optional date and location of a tournament match."""

from dataclasses import dataclass
from datetime import date

from server.core.entities.match import Match
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class MatchScheduleInput:
    scheduled_date: date | None = None
    location: str | None = None


class ScheduleMatch:
    def __init__(
        self,
        tournaments: TournamentRepository,
        matches: MatchRepository,
    ) -> None:
        self._get_tournament = GetTournament(tournaments)
        self._matches = matches

    def execute(
        self,
        tournament_id: str,
        match_id: str,
        data: MatchScheduleInput,
    ) -> Match:
        self._get_tournament.execute(tournament_id).ensure_accepts_schedule()
        match = self._matches.get(match_id)
        if match is None or match.tournament_id != tournament_id:
            raise InvalidTournamentError("Partida não encontrada.")
        scheduled = match.schedule(
            scheduled_date=data.scheduled_date,
            location=data.location,
        )
        self._matches.update(scheduled)
        return scheduled
