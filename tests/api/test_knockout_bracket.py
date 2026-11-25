import json

from server.app import create_app


def _create_tournament_with_teams(path, team_names):
    client = create_app(path).test_client()
    assert (
        client.post(
            "/tournaments",
            data={"name": "Copa", "format": "knockout"},
        ).status_code
        == 302
    )
    for name in team_names:
        assert client.post("/teams/", data={"name": name}).status_code == 302

    document = json.loads(path.read_text(encoding="utf-8"))
    tournament_id = document["tournaments"][0]["id"]
    team_ids = [team["id"] for team in document["teams"]]
    registration_url = f"/tournaments/{tournament_id}/teams"
    for team_id in team_ids:
        assert (
            client.post(
                registration_url,
                data={"team_id": team_id},
            ).status_code
            == 302
        )
    return client, tournament_id, team_ids


def test_knockout_bracket_view_shows_rounds_and_automatically_advanced_bye(
    tmp_path,
):
    path = tmp_path / "data.json"
    client, tournament_id, team_ids = _create_tournament_with_teams(
        path,
        ["Águias", "Tigres", "Leões"],
    )
    generation = {
        "order_mode": "manual",
        "bye_strategy": "performance",
        **{
            f"team_order_{team_id}": str(position)
            for position, team_id in enumerate(team_ids, start=1)
        },
    }

    generated = client.post(
        f"/tournaments/{tournament_id}/knockout/generate",
        data=generation,
    )

    assert generated.status_code == 302
    response_text = client.get(
        f"/tournaments/{tournament_id}",
    ).get_data(as_text=True)
    detail = " ".join(response_text.split())
    assert "Fase 1" in detail
    assert "Fase 2" in detail
    assert "Avançou por bye" in detail
    assert "Águias" in detail
    assert "Águias × A definir" in detail
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["tournaments"][0]["knockout"]["bye_team_ids"] == [
        team_ids[0],
    ]


def test_knockout_start_route_rejects_missing_bracket(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id, _ = _create_tournament_with_teams(
        path,
        ["Águias", "Tigres"],
    )

    response = client.post(
        f"/tournaments/{tournament_id}/knockout/start",
    )

    assert response.status_code == 400
    assert "chaveamento" in response.get_data(as_text=True)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["tournaments"][0]["status"] == "draft"


def test_knockout_generation_rejects_duplicate_manual_positions(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id, team_ids = _create_tournament_with_teams(
        path,
        ["Águias", "Tigres", "Leões"],
    )
    generation = {
        "order_mode": "manual",
        "bye_strategy": "performance",
        **{f"team_order_{team_id}": "1" for team_id in team_ids},
    }

    response = client.post(
        f"/tournaments/{tournament_id}/knockout/generate",
        data=generation,
    )

    assert response.status_code == 400
    assert "posição manual única" in response.get_data(as_text=True)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert "knockout" not in document["tournaments"][0]
    assert document.get("matches", []) == []
