import pytest

from server.core.entities.team import Team
from server.core.errors import TeamInStartedTournamentError, TeamNotFoundError
from server.core.use_cases.delete_team import DeleteTeam
from tests.fakes import (
    FakeTeamParticipationQuery,
    InMemoryRegistrationRepository,
)


@pytest.fixture
def registrations(team_repository) -> InMemoryRegistrationRepository:
    team_repository.add(Team.create(id="e1", name="Flamengo"))
    team_repository.add(Team.create(id="e2", name="Grêmio"))
    repository = InMemoryRegistrationRepository(team_repository)
    repository.add("copa", "e1")
    repository.add("copa", "e2")
    repository.add("liga", "e1")
    return repository


def _delete_team(team_repository, registrations, started=frozenset()):
    return DeleteTeam(
        team_repository,
        FakeTeamParticipationQuery(started),
        registrations,
    )


def test_delete_team_removes_only_that_team(team_repository, registrations):
    _delete_team(team_repository, registrations).execute("e1")

    assert team_repository.get("e1") is None
    assert team_repository.get("e2") is not None


def test_delete_team_removes_its_registrations_in_every_tournament(
    team_repository, registrations
):
    _delete_team(team_repository, registrations).execute("e1")

    assert registrations.team_ids("copa") == {"e2"}
    assert registrations.team_ids("liga") == set()


def test_delete_team_is_blocked_while_team_is_in_started_tournament(
    team_repository, registrations
):
    with pytest.raises(TeamInStartedTournamentError):
        _delete_team(team_repository, registrations, {"e1"}).execute("e1")

    assert team_repository.get("e1") is not None
    assert registrations.team_ids("copa") == {"e1", "e2"}
    assert registrations.team_ids("liga") == {"e1"}


def test_delete_team_rejects_unknown_id(team_repository, registrations):
    with pytest.raises(TeamNotFoundError):
        _delete_team(team_repository, registrations).execute("missing")
