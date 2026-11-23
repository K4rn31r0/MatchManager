from dataclasses import replace

import pytest

from server.core.entities.team import Team
from server.core.entities.tournament import TournamentFormat, TournamentStatus
from server.core.errors import (
    DomainError,
    DuplicateTeamNameError,
    InvalidTournamentError,
    TeamNotFoundError,
)
from server.core.use_cases.create_team import CreateTeam
from server.core.use_cases.create_tournament import (
    CreateTournament,
    CreateTournamentInput,
)
from server.core.use_cases.get_team import GetTeam
from server.core.use_cases.get_tournament import GetTournament
from server.core.use_cases.list_teams import ListTeams
from server.core.use_cases.team_data import TeamData
from server.core.use_cases.tournament_registrations import TournamentRegistrations
from tests.fakes import FakeClock, InMemoryTeamRepository, SequentialIdGenerator


class InMemoryRegistrations:
    def __init__(self, teams: InMemoryTeamRepository) -> None:
        self.teams = teams
        self.entries: set[tuple[str, str]] = set()

    def team_ids(self, tournament_id: str) -> set[str]:
        return {team for event, team in self.entries if event == tournament_id}

    def add(self, tournament_id: str, team_id: str) -> None:
        self.entries.add((tournament_id, team_id))

    def add_new_team(self, tournament_id: str, team: Team) -> None:
        self.teams.add(team)
        self.add(tournament_id, team.id)

    def remove(self, tournament_id: str, team_id: str) -> None:
        self.entries.remove((tournament_id, team_id))


@pytest.fixture
def setup(tournament_repository):
    teams = InMemoryTeamRepository()
    create_team = CreateTeam(teams, SequentialIdGenerator("team"))
    existing = create_team.execute(TeamData(name="Águias"))
    create_tournament = CreateTournament(
        tournament_repository, SequentialIdGenerator(), FakeClock()
    )
    first, second = [
        create_tournament.execute(
            CreateTournamentInput(
                name=name, tournament_format=TournamentFormat.KNOCKOUT
            )
        )
        for name in ["Copa", "Liga"]
    ]
    use_cases = TournamentRegistrations(
        InMemoryRegistrations(teams),
        GetTournament(tournament_repository),
        GetTeam(teams),
        ListTeams(teams),
        create_team,
    )
    return use_cases, teams, existing, first, second


def test_team_can_join_multiple_tournaments_but_only_once_per_tournament(setup):
    use_cases, _, team, first, second = setup
    use_cases.add(first.id, team.id)
    assert use_cases.list(second.id).available == [team]
    use_cases.add(second.id, team.id)
    with pytest.raises(DomainError, match="já está inscrita"):
        use_cases.add(first.id, team.id)
    assert use_cases.list(first.id).registered == [team]
    assert use_cases.list(first.id).available == []
    assert use_cases.list(second.id).registered == [team]


def test_create_and_register_reuses_team_validation_and_updates_both_lists(setup):
    use_cases, teams, existing, first, second = setup
    with pytest.raises(DuplicateTeamNameError):
        use_cases.create_and_add(first.id, TeamData(name="AGUIAS"))
    assert use_cases.list(first.id).registered == []
    new_team = use_cases.create_and_add(first.id, TeamData(name="Tigres"))
    assert new_team.abbreviation == "TIG"
    assert teams.get(new_team.id) == new_team
    assert use_cases.list(first.id).registered == [new_team]
    assert use_cases.list(first.id).available == [existing]
    assert new_team in use_cases.list(second.id).available


def test_remove_keeps_global_team_and_other_registration(setup):
    use_cases, teams, team, first, second = setup
    use_cases.add(first.id, team.id)
    use_cases.add(second.id, team.id)
    use_cases.remove(first.id, team.id)
    assert use_cases.list(first.id).registered == []
    assert use_cases.list(first.id).available == [team]
    assert use_cases.list(second.id).registered == [team]
    assert teams.get(team.id) == team


def test_add_rejects_unknown_team(setup):
    use_cases, _, _, first, _ = setup
    with pytest.raises(TeamNotFoundError):
        use_cases.add(first.id, "missing")
    assert use_cases.list(first.id).registered == []


@pytest.mark.parametrize(
    "status", [TournamentStatus.IN_PROGRESS, TournamentStatus.FINISHED]
)
def test_started_tournament_rejects_all_registration_changes(
    setup, tournament_repository, status,
):
    use_cases, teams, team, first, _ = setup
    use_cases.add(first.id, team.id)
    other = use_cases.create_and_add(first.id, TeamData(name="Tigres"))
    use_cases.remove(first.id, other.id)
    tournament_repository.update(replace(first, status=status))
    with pytest.raises(InvalidTournamentError):
        use_cases.add(first.id, other.id)
    with pytest.raises(InvalidTournamentError):
        use_cases.remove(first.id, team.id)
    with pytest.raises(InvalidTournamentError):
        use_cases.create_and_add(first.id, TeamData(name="Leões"))
    assert use_cases.list(first.id).registered == [team]
    assert teams.list_all() == [team, other]
