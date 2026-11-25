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

    @abstractmethod
    def get(self, tournament_id: str) -> Tournament | None:
        """Return a tournament by id, if present."""

    @abstractmethod
    def update(self, tournament: Tournament) -> None:
        """Replace an existing tournament."""

    @abstractmethod
    def delete(self, tournament_id: str) -> None:
        """Remove only the tournament record.

        Removing its registrations and matches is decided by the
        DeleteTournament use case.
        """

    @abstractmethod
    def participant_counts(self) -> dict[str, int]:
        """Return registration counts keyed by tournament ID."""
