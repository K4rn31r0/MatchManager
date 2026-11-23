from datetime import datetime

from server.core.entities.tournament import Tournament, TournamentFormat
from server.core.use_cases.list_tournaments import ListTournaments


def _tournament(
    tournament_id: str, name: str, created_at: datetime
) -> Tournament:
    return Tournament.create_draft(
        id=tournament_id,
        name=name,
        tournament_format=TournamentFormat.ROUND_ROBIN,
        created_at=created_at,
    )


def test_list_tournaments_returns_empty_list_when_none_exist(
    tournament_repository,
):
    assert ListTournaments(tournament_repository).execute() == []


def test_list_tournaments_returns_most_recently_created_first(
    tournament_repository,
):
    older = _tournament("t1", "Copa Antiga", datetime(2026, 1, 1, 10, 0))
    newest = _tournament("t2", "Copa Nova", datetime(2026, 3, 1, 10, 0))
    middle = _tournament("t3", "Copa do Meio", datetime(2026, 2, 1, 10, 0))
    for tournament in (older, newest, middle):
        tournament_repository.add(tournament)

    result = ListTournaments(tournament_repository).execute()

    assert [t.name for t in result] == [
        "Copa Nova",
        "Copa do Meio",
        "Copa Antiga",
    ]
