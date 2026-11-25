"""Persistence contract for tournament registrations."""

from typing import Protocol

from server.core.entities.team import Team


class RegistrationRepository(Protocol):
    def team_ids(self, tournament_id: str) -> set[str]:
        """Return the IDs of teams registered in the tournament."""

    def add(self, tournament_id: str, team_id: str) -> None:
        """Register an existing team."""

    def add_new_team(self, tournament_id: str, team: Team) -> None:
        """Persist a new team and its registration together."""

    def remove(self, tournament_id: str, team_id: str) -> None:
        """Remove the registration while keeping the team."""

    def remove_all_for_tournament(self, tournament_id: str) -> None:
        """Remove every registration of the tournament."""

    def remove_all_for_team(self, team_id: str) -> None:
        """Remove every registration of the team, in all tournaments."""
