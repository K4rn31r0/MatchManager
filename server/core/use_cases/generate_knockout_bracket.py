"""Generate and persist a knockout tournament bracket."""

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from server.core.entities.knockout_bracket import (
    KnockoutBracket,
    KnockoutRound,
    bracket_size,
    build_knockout_bracket,
)
from server.core.entities.tournament import (
    KnockoutByeStrategy,
    KnockoutConfig,
    KnockoutOrderMode,
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.registration_repository import (
    RegistrationRepository,
)
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class KnockoutBracketInput:
    order_mode: KnockoutOrderMode
    initial_order: tuple[str, ...] = ()
    bye_strategy: KnockoutByeStrategy = KnockoutByeStrategy.PERFORMANCE
    bye_team_ids: tuple[str, ...] = ()


class GenerateKnockoutBracket:
    def __init__(
        self,
        tournaments: TournamentRepository,
        registrations: RegistrationRepository,
        matches: MatchRepository,
        id_generator: Callable[[], str] | None = None,
        shuffle: Callable[[list[str]], None] | None = None,
        sample: Callable[[Sequence[str], int], list[str]] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._get_tournament = GetTournament(tournaments)
        self._tournaments = tournaments
        self._registrations = registrations
        self._matches = matches
        self._id_generator = id_generator or (lambda: uuid4().hex)
        self._shuffle = shuffle or random.shuffle
        self._sample = sample or random.sample
        self._clock = clock or datetime.now

    def execute(
        self,
        tournament_id: str,
        data: KnockoutBracketInput,
    ) -> KnockoutBracket:
        tournament = self._get_tournament.execute(tournament_id)
        self._ensure_tournament_is_configurable(tournament)
        registered_ids = self._registrations.team_ids(tournament_id)
        if len(registered_ids) < 2:
            raise InvalidTournamentError(
                "É necessário inscrever pelo menos duas equipes."
            )

        initial_order = self._resolve_initial_order(
            registered_ids, data.order_mode, data.initial_order,
        )
        bye_count = bracket_size(len(initial_order)) - len(initial_order)
        bye_ids = self._resolve_byes(initial_order, bye_count, data)
        bracket = build_knockout_bracket(
            tournament_id,
            initial_order,
            bye_ids,
            self._id_generator,
        )
        updated = tournament.configure_knockout(
            config=KnockoutConfig(
                order_mode=data.order_mode,
                initial_order=tuple(initial_order),
                bye_strategy=data.bye_strategy,
                bye_team_ids=tuple(bye_ids),
            ),
            updated_at=self._clock(),
        )
        self._matches.replace_for_tournament(
            tournament_id,
            [
                match
                for round_data in bracket.rounds
                for match in round_data.matches
            ],
        )
        self._tournaments.update(updated)
        return bracket

    @staticmethod
    def _ensure_tournament_is_configurable(tournament: Tournament) -> None:
        if tournament.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError(
                "Só é possível gerar o chaveamento em torneios em rascunho."
            )
        if tournament.tournament_format is not TournamentFormat.KNOCKOUT:
            raise InvalidTournamentError(
                "O chaveamento exige o formato mata-mata."
            )

    def _resolve_initial_order(
        self,
        registered_ids: set[str],
        order_mode: KnockoutOrderMode,
        requested_order: tuple[str, ...],
    ) -> list[str]:
        if order_mode is KnockoutOrderMode.MANUAL:
            if (
                len(requested_order) != len(registered_ids)
                or set(requested_order) != registered_ids
            ):
                raise InvalidTournamentError(
                    "A ordem manual deve incluir cada equipe inscrita uma vez."
                )
            return list(requested_order)
        if order_mode is not KnockoutOrderMode.DRAW:
            raise InvalidTournamentError("Escolha uma ordem inicial válida.")
        initial_order = sorted(registered_ids)
        self._shuffle(initial_order)
        return initial_order

    def _resolve_byes(
        self,
        initial_order: list[str],
        bye_count: int,
        data: KnockoutBracketInput,
    ) -> list[str]:
        if data.bye_strategy is KnockoutByeStrategy.PERFORMANCE:
            return initial_order[:bye_count]
        if data.bye_strategy is KnockoutByeStrategy.MANUAL:
            chosen = list(data.bye_team_ids)
            if (
                len(chosen) != bye_count
                or len(set(chosen)) != len(chosen)
                or not set(chosen).issubset(initial_order)
            ):
                raise InvalidTournamentError(
                    f"Selecione exatamente {bye_count} equipes para os byes."
                )
            chosen_set = set(chosen)
            return [
                team_id for team_id in initial_order if team_id in chosen_set
            ]
        if data.bye_strategy is KnockoutByeStrategy.DRAW:
            chosen = self._sample(initial_order, bye_count)
            if (
                len(chosen) != bye_count
                or len(set(chosen)) != bye_count
                or not set(chosen).issubset(initial_order)
            ):
                raise InvalidTournamentError(
                    "O sorteio de byes não foi válido."
                )
            chosen_set = set(chosen)
            return [
                team_id for team_id in initial_order if team_id in chosen_set
            ]
        raise InvalidTournamentError("Escolha uma estratégia de bye válida.")
