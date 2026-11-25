"""List the matches of any tournament, filtered by round and status."""

from dataclasses import dataclass

from server.core.entities.match import Match, MatchStatus
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class MatchFilter:
    """Optional criteria; a missing criterion accepts every match.

    ``round_number`` is the round in round-robin and the phase in knockout.
    """

    round_number: int | None = None
    status: MatchStatus | None = None

    def accepts(self, match: Match) -> bool:
        return (
            (self.round_number is None
             or match.round_number == self.round_number)
            and (self.status is None or match.status is self.status)
        )


@dataclass(frozen=True)
class TournamentMatches:
    matches: tuple[Match, ...]
    rounds: tuple[int, ...]
    total: int
    pending: int


class ListTournamentMatches:
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
        match_filter: MatchFilter | None = None,
    ) -> TournamentMatches:
        """Return the matches ordered by round and position.

        ``rounds`` lists every round of the tournament, regardless of the
        filter, so callers can offer it as a filter option.
        """
        self._get_tournament.execute(tournament_id)
        criteria = match_filter or MatchFilter()
        every_match = sorted(
            self._matches.list_for_tournament(tournament_id),
            key=lambda match: (
                match.round_number, match.bracket_position or 0, match.id,
            ),
        )
        return TournamentMatches(
            matches=tuple(
                match for match in every_match if criteria.accepts(match)
            ),
            rounds=tuple(
                sorted({match.round_number for match in every_match})
            ),
            total=len(every_match),
            pending=sum(
                match.status is MatchStatus.PENDING for match in every_match
            ),
        )
