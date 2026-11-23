from dataclasses import replace

import pytest

from server.core.entities.tournament import TournamentFormat, TournamentStatus
from server.core.errors import (
    DuplicateTournamentNameError,
    InvalidTournamentError,
    TournamentNotFoundError,
)
from server.core.use_cases.create_tournament import (
    CreateTournament,
    CreateTournamentInput,
)
from server.core.use_cases.delete_tournament import DeleteTournament
from server.core.use_cases.get_tournament import GetTournament
from server.core.use_cases.list_tournaments import ListTournaments
from server.core.use_cases.update_tournament import UpdateTournament
from tests.fakes import FakeClock, SequentialIdGenerator


def data(name):
    return CreateTournamentInput(
        name=name, tournament_format=TournamentFormat.KNOCKOUT
    )


@pytest.fixture
def seeded(tournament_repository):
    clock = FakeClock()
    create = CreateTournament(tournament_repository, SequentialIdGenerator(), clock)
    copa = create.execute(data("Copa São João"))
    liga = create.execute(data("Liga"))
    return copa, liga, clock


def test_update_keeps_identity_and_changes_order(tournament_repository, seeded):
    copa, liga, clock = seeded
    updated = UpdateTournament(tournament_repository, clock).execute(
        copa.id, data("  COPA São João  ")
    )
    assert updated.name == "COPA São João"
    assert updated.created_at == copa.created_at
    assert GetTournament(tournament_repository).execute(copa.id) == updated
    assert ListTournaments(tournament_repository).execute() == [updated, liga]


def test_update_rejects_name_used_by_another_tournament(tournament_repository, seeded):
    copa, liga, clock = seeded
    with pytest.raises(DuplicateTournamentNameError):
        UpdateTournament(tournament_repository, clock).execute(
            liga.id, data("COPA SAO JOAO")
        )
    assert GetTournament(tournament_repository).execute(liga.id) == liga


@pytest.mark.parametrize("status", [TournamentStatus.IN_PROGRESS, TournamentStatus.FINISHED])
def test_update_rejects_started_tournament(tournament_repository, seeded, status):
    copa, _, clock = seeded
    started = replace(copa, status=status)
    tournament_repository.update(started)
    with pytest.raises(InvalidTournamentError):
        UpdateTournament(tournament_repository, clock).execute(copa.id, data("Nova"))
    assert GetTournament(tournament_repository).execute(copa.id) == started


@pytest.mark.parametrize("status", list(TournamentStatus))
def test_list_combines_search_and_status(tournament_repository, seeded, status):
    copa, _, _ = seeded
    target = replace(copa, status=status)
    tournament_repository.update(target)
    listing = ListTournaments(tournament_repository)
    assert listing.execute(" SAO ", status) == [target]
    assert listing.execute("inexistente", status) == []
    assert listing.execute("SAO", next(item for item in TournamentStatus if item != status)) == []


@pytest.mark.parametrize("status", list(TournamentStatus))
def test_delete_requires_confirmation_in_every_status(tournament_repository, seeded, status):
    copa, _, _ = seeded
    target = replace(copa, status=status)
    tournament_repository.update(target)
    delete = DeleteTournament(tournament_repository)
    with pytest.raises(InvalidTournamentError):
        delete.execute(copa.id, confirmed=False)
    assert GetTournament(tournament_repository).execute(copa.id) == target
    delete.execute(copa.id, confirmed=True)
    with pytest.raises(TournamentNotFoundError):
        GetTournament(tournament_repository).execute(copa.id)
