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
