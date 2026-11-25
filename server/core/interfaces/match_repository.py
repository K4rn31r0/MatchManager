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

    def get(self, match_id: str) -> Match | None:
        """Return a match by id."""

    def list_for_tournament(self, tournament_id: str) -> list[Match]:
        """Return all matches belonging to a tournament."""

    def update(self, match: Match) -> None:
        """Replace an existing match."""

    def delete_for_tournament(self, tournament_id: str) -> None:
        """Remove every match of the tournament."""
