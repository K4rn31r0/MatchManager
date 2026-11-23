from datetime import date

import pytest

from server.core.entities.tournament import (
    TournamentFormat,
    TournamentStatus,
)
from server.core.errors import (
    DuplicateTournamentNameError,
    InvalidTournamentError,
)
from server.core.use_cases.create_tournament import (
    CreateTournament,
    CreateTournamentInput,
)
from tests.fakes import FakeClock, SequentialIdGenerator


@pytest.fixture
def create_tournament(tournament_repository) -> CreateTournament:
    return CreateTournament(
        repository=tournament_repository,
        id_generator=SequentialIdGenerator(),
        clock=FakeClock(),
    )


def test_create_tournament_with_valid_data_starts_as_draft(
    create_tournament, tournament_repository
):
    tournament = create_tournament.execute(
        CreateTournamentInput(
            name="Copa da PUC",
            tournament_format=TournamentFormat.ROUND_ROBIN,
            modality="Futsal",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 6, 30),
        )
    )

    assert tournament.name == "Copa da PUC"
    assert tournament.status == TournamentStatus.DRAFT
    assert tournament.tournament_format == TournamentFormat.ROUND_ROBIN
    assert tournament.modality == "Futsal"
    assert tournament_repository.list_all() == [tournament]


def test_create_tournament_without_optional_fields(create_tournament):
    tournament = create_tournament.execute(
        CreateTournamentInput(
            name="Torneio Relâmpago",
            tournament_format=TournamentFormat.KNOCKOUT,
        )
    )

    assert tournament.modality is None
    assert tournament.start_date is None
    assert tournament.end_date is None


def test_create_tournament_treats_blank_modality_as_absent(create_tournament):
    tournament = create_tournament.execute(
        CreateTournamentInput(
            name="Copa",
            tournament_format=TournamentFormat.KNOCKOUT,
            modality="   ",
        )
    )

    assert tournament.modality is None


def test_create_tournament_preserves_name_as_typed_without_outer_spaces(
    create_tournament,
):
    tournament = create_tournament.execute(
        CreateTournamentInput(
            name="  COPA da Puc  ",
            tournament_format=TournamentFormat.ROUND_ROBIN,
        )
    )

    assert tournament.name == "COPA da Puc"


@pytest.mark.parametrize("name", ["", "   "])
def test_create_tournament_rejects_empty_name(
    create_tournament, tournament_repository, name
):
    with pytest.raises(InvalidTournamentError):
        create_tournament.execute(
            CreateTournamentInput(
                name=name, tournament_format=TournamentFormat.ROUND_ROBIN
            )
        )

    assert tournament_repository.list_all() == []


def test_create_tournament_rejects_end_date_before_start_date(
    create_tournament, tournament_repository
):
    with pytest.raises(InvalidTournamentError):
        create_tournament.execute(
            CreateTournamentInput(
                name="Copa",
                tournament_format=TournamentFormat.ROUND_ROBIN,
                start_date=date(2026, 6, 30),
                end_date=date(2026, 3, 1),
            )
        )

    assert tournament_repository.list_all() == []


def test_create_tournament_accepts_same_start_and_end_date(create_tournament):
    tournament = create_tournament.execute(
        CreateTournamentInput(
            name="Copa de um dia",
            tournament_format=TournamentFormat.KNOCKOUT,
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 10),
        )
    )

    assert tournament.start_date == tournament.end_date == date(2026, 5, 10)


@pytest.mark.parametrize(
    "duplicate_name",
    [
        "Copa São Paulo",
        "copa são paulo",
        "COPA SÃO PAULO",
        "Copa Sao Paulo",
        "côpa sâo pãulo",
        "  Copa São Paulo  ",
    ],
)
def test_create_tournament_rejects_duplicate_name_ignoring_case_and_accents(
    create_tournament, tournament_repository, duplicate_name
):
    create_tournament.execute(
        CreateTournamentInput(
            name="Copa São Paulo",
            tournament_format=TournamentFormat.ROUND_ROBIN,
        )
    )

    with pytest.raises(DuplicateTournamentNameError):
        create_tournament.execute(
            CreateTournamentInput(
                name=duplicate_name,
                tournament_format=TournamentFormat.KNOCKOUT,
            )
        )

    assert len(tournament_repository.list_all()) == 1


def test_create_tournament_accepts_names_that_differ_in_letters(
    create_tournament, tournament_repository
):
    create_tournament.execute(
        CreateTournamentInput(
            name="Copa São Paulo",
            tournament_format=TournamentFormat.ROUND_ROBIN,
        )
    )
    create_tournament.execute(
        CreateTournamentInput(
            name="Copa São Paulo 2",
            tournament_format=TournamentFormat.ROUND_ROBIN,
        )
    )

    assert len(tournament_repository.list_all()) == 2
