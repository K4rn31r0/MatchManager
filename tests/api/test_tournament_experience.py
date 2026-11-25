"""Web experience of a tournament: tabs, filters, schedule (issue 10)."""

import json
import re

from server.app import create_app


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _started_round_robin(path, team_names):
    client = create_app(path).test_client()
    client.post(
        "/tournaments",
        data={"name": "Liga", "format": "round_robin"},
    )
    for name in team_names:
        client.post("/teams/", data={"name": name})
    document = _load(path)
    tournament_id = document["tournaments"][0]["id"]
    for team in document["teams"]:
        client.post(
            f"/tournaments/{tournament_id}/teams",
            data={"team_id": team["id"]},
        )
    client.post(
        f"/tournaments/{tournament_id}/round-robin/configure",
        data={
            "mode": "single",
            "tie_breaker_name": "Gols",
            "tie_breaker_direction": "positive",
            "statistic_fields": "Gols",
        },
    )
    assert (
        client.post(
            f"/tournaments/{tournament_id}/start",
        ).status_code
        == 302
    )
    return client, tournament_id


def _match_cards(html):
    return re.findall(r'<h4 class="match-teams">(.*?)</h4>', html)


def test_draft_tournament_shows_tabs_and_empty_matches(tmp_path):
    client = create_app(tmp_path / "data.json").test_client()
    client.post("/tournaments", data={"name": "Liga", "format": "round_robin"})
    tournament_id = _load(tmp_path / "data.json")["tournaments"][0]["id"]

    html = client.get(f"/tournaments/{tournament_id}").get_data(as_text=True)

    assert 'href="#partidas"' in html
    assert 'href="#equipes"' in html
    assert 'href="#configuracao"' in html
    assert 'href="#classificacao"' not in html
    assert "As partidas serão geradas automaticamente" in html
    assert 'id="equipes" class="tab-panel" data-default' in html
    assert "<script" not in html


def test_started_round_robin_shows_standings_tab_and_matches_default(
    tmp_path,
):
    client, tournament_id = _started_round_robin(
        tmp_path / "data.json",
        ["Águias", "Tigres"],
    )

    html = client.get(f"/tournaments/{tournament_id}").get_data(as_text=True)

    assert 'href="#classificacao"' in html
    assert 'id="partidas" class="tab-panel" data-default' in html
    assert "Regras do torneio" in html
    assert "Encerrar torneio" in html
    assert "1 partida pendente" in html


def test_matches_can_be_filtered_by_round_and_status(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id = _started_round_robin(
        path,
        ["Águias", "Tigres", "Leões", "Lobos"],
    )
    document = _load(path)
    first_round = [m for m in document["matches"] if m["round"] == 1]
    client.post(
        f"/tournaments/{tournament_id}/matches/{first_round[0]['id']}/result",
        data={"result": "draw"},
    )
    address = f"/tournaments/{tournament_id}"

    assert len(_match_cards(client.get(address).get_data(as_text=True))) == 6
    by_round = client.get(f"{address}?round=1").get_data(as_text=True)
    assert len(_match_cards(by_round)) == 2
    assert "<h3>Rodada 1</h3>" in by_round
    assert "<h3>Rodada 2</h3>" not in by_round
    assert '<option value="2">Rodada 2</option>' in by_round
    completed = client.get(
        f"{address}?match_status=completed",
    ).get_data(as_text=True)
    assert len(_match_cards(completed)) == 1
    assert "Empate" in completed
    pending_round_one = client.get(
        f"{address}?round=1&match_status=pending",
    ).get_data(as_text=True)
    assert len(_match_cards(pending_round_one)) == 1
    unknown_round = client.get(f"{address}?round=9").get_data(as_text=True)
    assert _match_cards(unknown_round) == []


def test_filter_without_matches_shows_empty_state(tmp_path):
    client, tournament_id = _started_round_robin(
        tmp_path / "data.json",
        ["Águias", "Tigres"],
    )

    html = client.get(
        f"/tournaments/{tournament_id}?match_status=completed",
    ).get_data(as_text=True)

    assert _match_cards(html) == []
    assert "Nenhuma partida encontrada com esses filtros." in html
    assert "Limpar" in html


def test_invalid_filter_shows_portuguese_message(tmp_path):
    client, tournament_id = _started_round_robin(
        tmp_path / "data.json",
        ["Águias", "Tigres"],
    )

    html = client.get(
        f"/tournaments/{tournament_id}?round=abc",
    ).get_data(as_text=True)

    assert "Filtro de partidas inválido" in html
    assert len(_match_cards(html)) == 1


def test_match_date_and_location_are_optional_and_do_not_block_result(
    tmp_path,
):
    path = tmp_path / "data.json"
    client, tournament_id = _started_round_robin(path, ["Águias", "Tigres"])
    match_id = _load(path)["matches"][0]["id"]

    result = client.post(
        f"/tournaments/{tournament_id}/matches/{match_id}/result",
        data={"result": "first_win"},
    )
    assert result.status_code == 302
    assert result.location.endswith("#partidas")

    scheduled = client.post(
        f"/tournaments/{tournament_id}/matches/{match_id}/schedule",
        data={"scheduled_date": "2026-12-05", "location": "Ginásio Central"},
    )
    assert scheduled.status_code == 302

    match = _load(path)["matches"][0]
    assert match["status"] == "completed"
    assert match["scheduled_date"] == "2026-12-05"
    assert match["location"] == "Ginásio Central"
    html = client.get(f"/tournaments/{tournament_id}").get_data(as_text=True)
    assert "05/12/2026 · Ginásio Central" in html

    cleared = client.post(
        f"/tournaments/{tournament_id}/matches/{match_id}/schedule",
        data={"scheduled_date": "", "location": ""},
    )
    assert cleared.status_code == 302
    match = _load(path)["matches"][0]
    assert "scheduled_date" not in match and "location" not in match
    assert match["status"] == "completed"


def test_invalid_match_date_shows_error_and_reopens_form(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id = _started_round_robin(path, ["Águias", "Tigres"])
    match_id = _load(path)["matches"][0]["id"]

    response = client.post(
        f"/tournaments/{tournament_id}/matches/{match_id}/schedule",
        data={"scheduled_date": "05/12", "location": "Ginásio"},
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Data de partida inválida." in html
    assert 'value="Ginásio"' in html


def test_invalid_result_keeps_typed_values_in_the_open_form(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id = _started_round_robin(path, ["Águias", "Tigres"])
    match_id = _load(path)["matches"][0]["id"]

    response = client.post(
        f"/tournaments/{tournament_id}/matches/{match_id}/result",
        data={"result": "first_win", "first_score": "3", "second_score": ""},
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Informe o placar completo" in html
    assert 'class="match-form" open' in html
    assert re.search(r'name="first_score"[^>]*value="3"', html)


def test_navigation_marks_the_current_section(tmp_path):
    client = create_app(tmp_path / "data.json").test_client()

    home = client.get("/").get_data(as_text=True)
    teams = client.get("/teams/").get_data(as_text=True)

    assert 'href="/" aria-current="page"' in home
    assert 'href="/teams/" aria-current="page"' in teams
    assert 'href="/teams/" aria-current="page"' not in home
