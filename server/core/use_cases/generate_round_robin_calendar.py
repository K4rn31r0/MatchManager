"""Generate round-robin fixtures and persist them."""

from dataclasses import dataclass

from server.core.entities.match import Match
from server.core.entities.tournament import (
    RoundRobinMode,
    Tournament,
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import InvalidTournamentError
from server.core.interfaces.match_repository import MatchRepository
from server.core.interfaces.registration_repository import RegistrationRepository
from server.core.interfaces.tournament_repository import TournamentRepository
from server.core.use_cases.get_tournament import GetTournament


@dataclass(frozen=True)
class RoundRobinFixture:
    first_team_id: str
    second_team_id: str


@dataclass(frozen=True)
class RoundRobinRound:
    number: int
    matches: tuple[RoundRobinFixture, ...]
    resting_team_ids: tuple[str, ...]


@dataclass(frozen=True)
class RoundRobinCalendar:
    rounds: tuple[RoundRobinRound, ...]


class GenerateRoundRobinCalendar:
    def __init__(
        self,
        tournament_repository: TournamentRepository,
        registrations: RegistrationRepository,
        matches: MatchRepository,
    ) -> None:
        self._get = GetTournament(tournament_repository)
        self._registrations = registrations
        self._matches = matches

    def execute(self, tournament_id: str) -> RoundRobinCalendar:
        tournament = self._get.execute(tournament_id)
        if tournament.status is not TournamentStatus.DRAFT:
            raise InvalidTournamentError(
                "Só é possível gerar o calendário em torneios em rascunho."
            )
        if tournament.tournament_format is not TournamentFormat.ROUND_ROBIN:
            raise InvalidTournamentError(
                "O calendário de pontos corridos exige o formato correspondente."
            )
        if tournament.round_robin is None:
            raise InvalidTournamentError(
                "Configure os pontos corridos antes de gerar o calendário."
            )
        team_ids = sorted(self._registrations.team_ids(tournament_id))
        if len(team_ids) < 2:
            raise InvalidTournamentError(
                "É necessário inscrever pelo menos duas equipes."
            )

        first_leg = _build_rounds(team_ids)
        legs = [first_leg]
        if tournament.round_robin.mode is RoundRobinMode.DOUBLE:
            legs.append(
                tuple(
                    RoundRobinRound(
                        number=round_data.number + len(first_leg),
                        matches=tuple(
                            RoundRobinFixture(
                                first_team_id=fixture.second_team_id,
                                second_team_id=fixture.first_team_id,
                            )
                            for fixture in round_data.matches
                        ),
                        resting_team_ids=round_data.resting_team_ids,
                    )
                    for round_data in first_leg
                )
            )
        rounds = tuple(round_data for leg in legs for round_data in leg)
        persisted: list[Match] = []
        fixture_index = 0
        for round_data in rounds:
            for fixture in round_data.matches:
                fixture_index += 1
                persisted.append(
                    Match(
                        id=f"{tournament_id}-{fixture_index}",
                        tournament_id=tournament_id,
                        round_number=round_data.number,
                        first_team_id=fixture.first_team_id,
                        second_team_id=fixture.second_team_id,
                    )
                )
        self._matches.replace_for_tournament(tournament_id, persisted)
        return RoundRobinCalendar(rounds=rounds)


def _build_rounds(team_ids: list[str]) -> tuple[RoundRobinRound, ...]:
    rotation: list[str | None] = list(team_ids)
    if len(rotation) % 2:
        rotation.append(None)

    rounds: list[RoundRobinRound] = []
    for round_number in range(1, len(rotation)):
        fixtures: list[RoundRobinFixture] = []
        resting: list[str] = []
        for index in range(len(rotation) // 2):
            first = rotation[index]
            second = rotation[-index - 1]
            if first is None:
                resting.append(second or "")
            elif second is None:
                resting.append(first)
            else:
                fixtures.append(
                    RoundRobinFixture(
                        first_team_id=first,
                        second_team_id=second,
                    )
                )
        rounds.append(
            RoundRobinRound(
                number=round_number,
                matches=tuple(fixtures),
                resting_team_ids=tuple(team for team in resting if team),
            )
        )
        rotation = [rotation[0], rotation[-1], *rotation[1:-1]]
    return tuple(rounds)
