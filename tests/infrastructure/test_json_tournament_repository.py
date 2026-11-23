from datetime import date, datetime

from server.core.entities.tournament import (
    RoundRobinConfig,
    RoundRobinMode,
    TieBreaker,
    TieBreakerDirection,
    Tournament,
    TournamentFormat,
)
from server.infrastructure.db.json_file_storage import JsonFileStorage
from server.infrastructure.db.json_tournament_repository import (
    JsonTournamentRepository,
)


def _repository(path) -> JsonTournamentRepository:
    return JsonTournamentRepository(JsonFileStorage(path))


def test_list_all_is_empty_when_file_does_not_exist(tmp_path):
    repository = _repository(tmp_path / "data.json")

    assert repository.list_all() == []


def test_added_tournament_is_recovered_by_a_new_repository_instance(tmp_path):
    path = tmp_path / "data.json"
    tournament = Tournament.create_draft(
        id="t1",
        name="Copa São Paulo",
        tournament_format=TournamentFormat.KNOCKOUT,
        created_at=datetime(2026, 1, 1, 12, 30),
        modality="Vôlei",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 6, 30),
    )

    _repository(path).add(tournament)

    assert _repository(path).list_all() == [tournament]


def test_tournament_without_optional_fields_round_trips(tmp_path):
    path = tmp_path / "data.json"
    tournament = Tournament.create_draft(
        id="t1",
        name="Copa",
        tournament_format=TournamentFormat.ROUND_ROBIN,
        created_at=datetime(2026, 1, 1, 12, 30),
    )

    _repository(path).add(tournament)

    assert _repository(path).list_all() == [tournament]


def test_round_robin_configuration_round_trips(tmp_path):
    tournament = Tournament.create_draft(
        id="t1",
        name="Liga",
        tournament_format=TournamentFormat.ROUND_ROBIN,
        created_at=datetime(2026, 1, 1, 12, 30),
    )
    configured = tournament.configure_round_robin(
        config=RoundRobinConfig(
            mode=RoundRobinMode.DOUBLE,
            win_points=3,
            draw_points=1,
            loss_points=0,
            tie_breakers=(
                TieBreaker(
                    name="Saldo",
                    direction=TieBreakerDirection.POSITIVE,
                ),
                TieBreaker(
                    name="Cartões",
                    direction=TieBreakerDirection.NEGATIVE,
                ),
            ),
            statistic_fields=("Gols", "Cartões"),
        ),
        updated_at=datetime(2026, 1, 1, 12, 31),
    )

    _repository(tmp_path / "data.json").add(configured)

    assert _repository(tmp_path / "data.json").list_all() == [configured]
