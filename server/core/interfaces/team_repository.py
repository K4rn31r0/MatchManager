"""Persistence contract for teams required by the core."""

from abc import ABC, abstractmethod

from server.core.entities.team import Team


class TeamRepository(ABC):
    """Stores and retrieves teams."""

    @abstractmethod
    def add(self, team: Team) -> None:
        """Persist a new team."""

    @abstractmethod
    def get(self, team_id: str) -> Team | None:
        """Return the team with the given id, or None if it does not exist."""

    @abstractmethod
    def update(self, team: Team) -> None:
        """Replace the stored team that has the same id."""

    @abstractmethod
    def delete(self, team_id: str) -> None:
        """Remove the team with the given id."""

    @abstractmethod
    def list_all(self) -> list[Team]:
        """Return every persisted team."""
