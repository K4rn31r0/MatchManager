"""Start a knockout tournament only when its saved bracket is valid."""

from collections.abc import Callable
from datetime import datetime

from server.core.entities.knockout_bracket import (
    bracket_size,
    build_knockout_bracket,
)
from server.core.entities.match import Match, MatchStatus
from server.core.entities.tournament import (
    KnockoutByeStrategy,
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


class StartKnockoutTournament:
    def __init__(
        self,
        tournaments: TournamentRepository,
        registrations: RegistrationRepository,
        matches: MatchRepository,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._get_tournament = GetTournament(tournaments)
        self._tournaments = tournaments
        self._registrations = registrations
        self._matches = matches
        self._clock = clock or datetime.now

    def execute(self, tournament_id: str) -> Tournament:
        tournament = self._get_tournament.execute(tournament_id)
        self._ensure_draft_knockout(tournament)
        registrations = self._registrations.team_ids(tournament_id)
        if len(registrations) < 2:
            raise InvalidTournamentError(
                "É necessário inscrever pelo menos duas equipes."
            )

        config = tournament.knockout
        if config is None or (
            len(config.initial_order) != len(registrations)
            or set(config.initial_order) != registrations
        ):
            raise InvalidTournamentError(
                "Gere um chaveamento válido antes de iniciar o torneio."
            )
        expected_byes = bracket_size(len(registrations)) - len(registrations)
        if (
            len(config.bye_team_ids) != expected_byes
            or len(set(config.bye_team_ids)) != expected_byes
            or not set(config.bye_team_ids).issubset(registrations)
        ):
            raise InvalidTournamentError(
                "Gere um chaveamento válido antes de iniciar o torneio."
            )
        if (
            config.bye_strategy is KnockoutByeStrategy.PERFORMANCE
            and config.bye_team_ids != config.initial_order[:expected_byes]
        ):
            raise InvalidTournamentError(
                "Gere um chaveamento válido antes de iniciar o torneio."
            )

        matches = self._matches.list_for_tournament(tournament_id)
        expected = build_knockout_bracket(
            tournament_id,
            list(config.initial_order),
            list(config.bye_team_ids),
            _unused_match_id,
        )
        expected_slots = {
            _match_slot(match)
            for round_data in expected.rounds
            for match in round_data.matches
        }
        actual_slots = {_match_slot(match) for match in matches}
        if (
            len(matches) != len(actual_slots)
            or len({match.id for match in matches}) != len(matches)
            or actual_slots != expected_slots
            or any(
                match.status is not MatchStatus.PENDING
                or match.result is not None
                or match.first_score is not None
                or match.second_score is not None
                or match.first_team_stats is not None
                or match.second_team_stats is not None
                for match in matches
            )
        ):
            raise InvalidTournamentError(
                "Gere um chaveamento válido antes de iniciar o torneio."
            )

        started = tournament.start_knockout(self._clock())
        self._tournaments.update(started)
        return started

    @staticmethod
    def _ensure_draft_knockout(tournament: Tournament) -> None:
        if tournament.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError(
                "Só é possível iniciar torneios em rascunho."
            )
        if tournament.tournament_format is not TournamentFormat.KNOCKOUT:
            raise InvalidTournamentError(
                "O início solicitado não corresponde ao formato do torneio."
            )


def _match_slot(
    match: Match,
) -> tuple[int, int | None, str | None, str | None]:
    return (
        match.round_number,
        match.bracket_position,
        match.first_team_id,
        match.second_team_id,
    )


def _unused_match_id() -> str:
    return ""
