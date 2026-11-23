"""Errors raised by the core when a business rule is violated.

Messages are user-facing and therefore written in Portuguese.
"""


class DomainError(Exception):
    """Base class for every business rule violation."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidTournamentError(DomainError):
    """Tournament data does not satisfy the tournament invariants."""


class DuplicateTournamentNameError(DomainError):
    """Another tournament already uses an equivalent name."""


class InvalidTeamError(DomainError):
    """Team data does not satisfy the team invariants."""


class DuplicateTeamNameError(DomainError):
    """Another team already uses an equivalent name."""


class TeamNotFoundError(DomainError):
    """No team exists with the requested id."""


class TeamInStartedTournamentError(DomainError):
    """The team cannot be removed while it plays a started tournament."""


class TournamentNotFoundError(DomainError):
    """No tournament exists with the requested id."""
