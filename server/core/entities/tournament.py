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


class RoundRobinMode(Enum):
    """How often teams face each other in a round-robin tournament."""

    SINGLE = "single"
    DOUBLE = "double"


class TieBreakerDirection(Enum):
    """Whether a tie-breaker favors higher or lower aggregate values."""

    POSITIVE = "positive"
    NEGATIVE = "negative"


class KnockoutOrderMode(Enum):
    MANUAL = "manual"
    DRAW = "draw"


class KnockoutByeStrategy(Enum):
    MANUAL = "manual"
    DRAW = "draw"
    PERFORMANCE = "performance"


@dataclass(frozen=True, kw_only=True)
class TieBreaker:
    name: str
    direction: TieBreakerDirection


@dataclass(frozen=True, kw_only=True)
class StatisticField:
    name: str


@dataclass(frozen=True, kw_only=True)
class RoundRobinConfig:
    mode: RoundRobinMode
    win_points: int
    draw_points: int
    loss_points: int
    tie_breakers: tuple[TieBreaker, ...]
    statistic_fields: tuple[StatisticField, ...] = ()


@dataclass(frozen=True, kw_only=True)
class KnockoutConfig:
    order_mode: KnockoutOrderMode
    initial_order: tuple[str, ...]
    bye_strategy: KnockoutByeStrategy
    bye_team_ids: tuple[str, ...]


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
    round_robin: RoundRobinConfig | None = None
    knockout: KnockoutConfig | None = None

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

    def ensure_registrations_open(self) -> None:
        if self.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError(
                "Só é possível alterar inscrições em torneios em rascunho."
            )

    def configure_round_robin(
        self,
        *,
        config: RoundRobinConfig,
        updated_at: datetime,
    ) -> "Tournament":
        if self.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError(
                "Só é possível configurar torneios em rascunho."
            )
        if self.tournament_format is not TournamentFormat.ROUND_ROBIN:
            raise InvalidTournamentError(
                "Esta configuração só pode ser usada em pontos corridos."
            )
        if not config.win_points > config.draw_points > config.loss_points:
            raise InvalidTournamentError(
                "A pontuação deve respeitar vitória maior que empate maior que derrota."
            )
        if not config.tie_breakers:
            raise InvalidTournamentError(
                "É necessário cadastrar pelo menos um critério de desempate."
            )
        return replace(self, round_robin=config, updated_at=updated_at)

    def configure_knockout(
        self,
        *,
        config: KnockoutConfig,
        updated_at: datetime,
    ) -> "Tournament":
        if self.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError(
                "Só é possível configurar torneios em rascunho."
            )
        if self.tournament_format is not TournamentFormat.KNOCKOUT:
            raise InvalidTournamentError(
                "Esta configuração só pode ser usada em mata-mata."
            )
        return replace(self, knockout=config, updated_at=updated_at)

    def start_knockout(self, started_at: datetime) -> "Tournament":
        if self.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError(
                "Só é possível iniciar torneios em rascunho."
            )
        if self.tournament_format is not TournamentFormat.KNOCKOUT:
            raise InvalidTournamentError(
                "O início solicitado não corresponde ao formato do torneio."
            )
        if self.knockout is None:
            raise InvalidTournamentError(
                "Gere um chaveamento válido antes de iniciar o torneio."
            )
        return replace(
            self,
            status=TournamentStatus.IN_PROGRESS,
            updated_at=started_at,
        )

    def has_equivalent_name(self, name: str) -> bool:
        """Tell whether a name clashes with this tournament's name.

        Names are equivalent when they differ only in case or accents.
        """
        return normalize_name(self.name) == normalize_name(name)

    def finish_round_robin(self, finished_at: datetime) -> "Tournament":
        if self.status is not TournamentStatus.IN_PROGRESS:
            raise InvalidTournamentError(
                "Só é possível encerrar torneios em andamento."
            )
        if self.tournament_format is not TournamentFormat.ROUND_ROBIN:
            raise InvalidTournamentError(
                "O encerramento solicitado não corresponde ao formato do torneio."
            )
        return replace(
            self,
            status=TournamentStatus.FINISHED,
            updated_at=finished_at,
        )
