"""List matches for a round-robin tournament."""

from server.core.entities.match import Match
from server.core.entities.tournament import TournamentFormat
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


class ListRoundRobinMatches:
    def __init__(
        self,
        tournament_repository: TournamentRepository,
        matches: MatchRepository,
    ) -> None:
        self._get = GetTournament(tournament_repository)
        self._matches = matches

    def execute(self, tournament_id: str) -> list[Match]:
        tournament = self._get.execute(tournament_id)
        if tournament.tournament_format is not TournamentFormat.ROUND_ROBIN:
            raise InvalidTournamentError(
                "A lista solicitada não corresponde a pontos corridos."
            )
        return self._matches.list_for_tournament(tournament_id)
