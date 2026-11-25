import json

from server.app import create_app


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _create_configured_round_robin(path, team_names):
    client = create_app(path).test_client()
    assert (
        client.post(
            "/tournaments",
            data={"name": "Liga", "format": "round_robin"},
        ).status_code
        == 302
    )
    for name in team_names:
        assert client.post("/teams/", data={"name": name}).status_code == 302
    document = _load(path)
    tournament_id = document["tournaments"][0]["id"]
    for team in document["teams"]:
        assert (
            client.post(
                f"/tournaments/{tournament_id}/teams",
                data={"team_id": team["id"]},
            ).status_code
            == 302
        )
    assert (
        client.post(
            f"/tournaments/{tournament_id}/round-robin/configure",
            data={
                "mode": "single",
                "tie_breaker_name": "Gols",
                "tie_breaker_direction": "positive",
            },
        ).status_code
        == 302
    )
    return client, tournament_id


def test_start_confirmation_shows_format_and_participants(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id = _create_configured_round_robin(
        path,
        ["Águias", "Tigres"],
    )

    page = client.get(f"/tournaments/{tournament_id}/start")

    text = page.get_data(as_text=True)
    assert page.status_code == 200
    assert "Pontos corridos" in text
    assert "Águias" in text and "Tigres" in text
    assert "Confirmar início" in text


def test_start_with_single_team_shows_error_and_keeps_draft(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id = _create_configured_round_robin(path, ["Águias"])

    response = client.post(f"/tournaments/{tournament_id}/start")

    assert response.status_code == 400
    assert "pelo menos duas equipes" in response.get_data(as_text=True)
    assert _load(path)["tournaments"][0]["status"] == "draft"


def test_round_robin_web_lifecycle_with_correction_after_finish(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id = _create_configured_round_robin(
        path,
        ["Águias", "Tigres"],
    )
    assert client.post("/teams/", data={"name": "Leões"}).status_code == 302

    assert (
        client.post(
            f"/tournaments/{tournament_id}/start",
        ).status_code
        == 302
    )

    document = _load(path)
    assert document["tournaments"][0]["status"] == "in_progress"
    assert len(document["matches"]) == 1
    outsider_id = next(
        team["id"] for team in document["teams"] if team["name"] == "Leões"
    )
    assert (
        client.post(
            f"/tournaments/{tournament_id}/teams",
            data={"team_id": outsider_id},
        ).status_code
        == 400
    )
    assert (
        client.get(
            f"/tournaments/{tournament_id}/start",
        ).status_code
        == 302
    )

    match_id = document["matches"][0]["id"]
    result_address = f"/tournaments/{tournament_id}/matches/{match_id}/result"
    finish_address = f"/tournaments/{tournament_id}/round-robin/finish"
    assert client.post(finish_address).status_code == 400
    assert (
        client.post(
            result_address,
            data={"result": "first_win"},
        ).status_code
        == 302
    )
    assert client.post(finish_address).status_code == 302

    corrected = client.post(result_address, data={"result": "second_win"})

    assert corrected.status_code == 302
    document = _load(path)
    assert document["tournaments"][0]["status"] == "finished"
    assert document["matches"][0]["result"] == "second_win"
    detail = client.get(f"/tournaments/{tournament_id}").get_data(
        as_text=True,
    )
    second_team_id = document["matches"][0]["second_team_id"]
    second_name = next(
        team["name"]
        for team in document["teams"]
        if team["id"] == second_team_id
    )
    assert f"Campeão: {second_name}" in detail
    assert "Configuração de pontos corridos" not in detail
