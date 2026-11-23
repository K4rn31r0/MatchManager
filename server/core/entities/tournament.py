"""Tournament entity and its value types."""

from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import Enum

from server.core.entities.names import normalize_name, optional_text
from server.core.errors import InvalidTournamentError


class TournamentFormat(Enum):
    """How the tournament decides its champion."""

    ROUND_ROBIN = "round_robin"
    KNOCKOUT = "knockout"


class TournamentStatus(Enum):
    """Lifecycle stage of a tournament."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


@dataclass(frozen=True, kw_only=True)
class Tournament:
    """A sports competition organized by the user.

    Instances are immutable: domain operations return new instances.
    """

    id: str
    name: str
    tournament_format: TournamentFormat
    status: TournamentStatus
    created_at: datetime
    modality: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    updated_at: datetime | None = None

    @property
    def last_activity(self) -> datetime:
        return self.updated_at or self.created_at

    def edit(
        self, *, name: str, tournament_format: TournamentFormat,
        modality: str | None, start_date: date | None,
        end_date: date | None, updated_at: datetime,
    ) -> "Tournament":
        if self.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError("Só é possível editar torneios em rascunho.")
        return replace(
            self, name=name.strip(), tournament_format=tournament_format,
            modality=optional_text(modality), start_date=start_date,
            end_date=end_date, updated_at=updated_at,
        )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidTournamentError("O nome do torneio é obrigatório.")
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise InvalidTournamentError(
                "A data de término não pode ser anterior à data de início."
            )

    @classmethod
    def create_draft(
        cls,
        *,
        id: str,
        name: str,
        tournament_format: TournamentFormat,
        created_at: datetime,
        modality: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> "Tournament":
        """Create a new tournament in the draft status.

        Surrounding whitespace is removed from the name, which is otherwise
        kept exactly as typed. A blank modality is treated as absent.
        """
        return cls(
            id=id,
            name=name.strip(),
            tournament_format=tournament_format,
            status=TournamentStatus.DRAFT,
            created_at=created_at,
            modality=optional_text(modality),
            start_date=start_date,
            end_date=end_date,
        )

    def has_equivalent_name(self, name: str) -> bool:
        """Tell whether a name clashes with this tournament's name.

        Names are equivalent when they differ only in case or accents.
        """
        return normalize_name(self.name) == normalize_name(name)
