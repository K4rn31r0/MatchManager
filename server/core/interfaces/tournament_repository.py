"""Persistence contract for tournaments required by the core."""

from abc import ABC, abstractmethod

from server.core.entities.tournament import Tournament


class TournamentRepository(ABC):
    """Stores and retrieves tournaments."""

    @abstractmethod
    def add(self, tournament: Tournament) -> None:
        """Persist a new tournament."""

    @abstractmethod
    def list_all(self) -> list[Tournament]:
        """Return every persisted tournament."""
