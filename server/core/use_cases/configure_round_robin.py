"""Use case for configuring a round-robin tournament."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from server.core.entities.tournament import (
    RoundRobinConfig,
    RoundRobinMode,
    StatisticField,
    TieBreaker,
    TieBreakerDirection,
    Tournament,
)
from server.core.errors import InvalidTournamentError
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class RoundRobinConfigInput:
    mode: RoundRobinMode
    win_points: int = 3
    draw_points: int = 1
    loss_points: int = 0
    tie_breakers: tuple[tuple[str, str], ...] = ()
    statistic_fields: tuple[str, ...] = ()


class ConfigureRoundRobin:
    def __init__(
        self,
        repository: TournamentRepository,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._get = GetTournament(repository)
        self._clock = clock or datetime.now

    def execute(
        self,
        tournament_id: str,
        data: RoundRobinConfigInput,
    ) -> Tournament:
        tournament = self._get.execute(tournament_id)
        tie_breakers = tuple(
            TieBreaker(
                name=name.strip(), direction=_parse_direction(direction)
            )
            for name, direction in data.tie_breakers
            if name.strip()
        )
        if len(tie_breakers) != len(data.tie_breakers):
            raise InvalidTournamentError(
                "Cada critério de desempate precisa de um nome."
            )
        statistics = tuple(
            StatisticField(name=name.strip())
            for name in data.statistic_fields
            if name.strip()
        )
        config = RoundRobinConfig(
            mode=data.mode,
            win_points=data.win_points,
            draw_points=data.draw_points,
            loss_points=data.loss_points,
            tie_breakers=tie_breakers,
            statistic_fields=statistics,
        )
        configured = tournament.configure_round_robin(
            config=config,
            updated_at=self._clock(),
        )
        self._repository.update(configured)
        return configured


def _parse_direction(value: str) -> TieBreakerDirection:
    try:
        return TieBreakerDirection(value)
    except ValueError:
        raise InvalidTournamentError(
            "O critério de desempate deve ser positivo ou negativo."
        ) from None
