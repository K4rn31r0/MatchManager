"""Persistence contract for tournament matches."""

from typing import Protocol

from server.core.entities.match import Match


class MatchRepository(Protocol):
    def replace_for_tournament(
        self,
        tournament_id: str,
        matches: list[Match],
    ) -> None:
        """Replace all matches for a tournament."""
