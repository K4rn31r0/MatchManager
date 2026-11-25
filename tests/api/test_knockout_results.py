import json

from server.app import create_app


def _create_started_knockout(path, team_names):
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
    for team_id in team_ids:
        assert (
            client.post(
                f"/tournaments/{tournament_id}/teams",
                data={"team_id": team_id},
            ).status_code
            == 302
        )

    generation = {
        "order_mode": "manual",
        "bye_strategy": "performance",
        **{
            f"team_order_{team_id}": str(position)
            for position, team_id in enumerate(team_ids, start=1)
        },
    }
    assert (
        client.post(
            f"/tournaments/{tournament_id}/knockout/generate",
            data=generation,
        ).status_code
        == 302
    )
    assert (
        client.post(
            f"/tournaments/{tournament_id}/knockout/start",
        ).status_code
        == 302
    )
    return client, tournament_id


def test_knockout_web_flow_shows_progress_to_final_and_champion(tmp_path):
    path = tmp_path / "data.json"
    client, tournament_id = _create_started_knockout(
        path,
        ["Águias", "Tigres", "Leões", "Lobos"],
    )
    document = json.loads(path.read_text(encoding="utf-8"))
    team_names = {team["id"]: team["name"] for team in document["teams"]}
    first_round = sorted(
        (match for match in document["matches"] if match["round"] == 1),
        key=lambda match: match["bracket_position"],
    )
    advanced_team_ids = [match["first_team_id"] for match in first_round]

    initial_detail = client.get(
        f"/tournaments/{tournament_id}",
    ).get_data(as_text=True)
    assert "Fase 1" in initial_detail
    assert "Fase 2" in initial_detail
    assert "Salvar resultado" in initial_detail

    for match in first_round:
        response = client.post(
            (
                f"/tournaments/{tournament_id}/knockout/matches/"
                f"{match['id']}/result"
            ),
            data={"result": "first_win"},
        )
        assert response.status_code == 302

    after_semifinals = " ".join(
        client.get(f"/tournaments/{tournament_id}")
        .get_data(as_text=True)
        .split()
    )
    final = next(
        match
        for match in json.loads(path.read_text(encoding="utf-8"))["matches"]
        if match["round"] == 2
    )
    final_card = (
        f"{team_names[advanced_team_ids[0]]} × "
        f"{team_names[advanced_team_ids[1]]}"
    )
    assert final_card in after_semifinals

    result = client.post(
        (
            f"/tournaments/{tournament_id}/knockout/matches/"
            f"{final['id']}/result"
        ),
        data={"result": "first_win"},
    )
    assert result.status_code == 302

    before_closing = client.get(f"/tournaments/{tournament_id}").get_data(
        as_text=True,
    )
    assert "Campeão:" not in before_closing
    closed = client.post(
        f"/tournaments/{tournament_id}/knockout/finish",
    )
    assert closed.status_code == 302
    after_closing = " ".join(
        client.get(f"/tournaments/{tournament_id}")
        .get_data(as_text=True)
        .split()
    )
    assert "Encerrado" in after_closing
    assert f"Campeão: {team_names[advanced_team_ids[0]]}" in after_closing
