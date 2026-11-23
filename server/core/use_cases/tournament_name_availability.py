"""Shared uniqueness rule for tournament names."""

from server.core.errors import DuplicateTournamentNameError
from server.core.interfaces.tournament_repository import TournamentRepository


def ensure_name_available(
    repository: TournamentRepository, name: str, excluding_id: str | None = None,
) -> None:
    if any(
        other.id != excluding_id and other.has_equivalent_name(name)
        for other in repository.list_all()
    ):
        raise DuplicateTournamentNameError(
            f"Já existe um torneio chamado “{name.strip()}”."
        )
