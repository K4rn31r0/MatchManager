import json

from server.app import create_app


def test_tournament_registrations_flow(tmp_path):
    path = tmp_path / "data.json"
    client = create_app(path).test_client()
    assert (
        client.post(
            "/tournaments",
            data={"name": "Copa", "format": "knockout"},
        ).status_code
        == 302
    )
    assert client.post("/teams/", data={"name": "Águias"}).status_code == 302

    document = json.loads(path.read_text())
    tournament_id = document["tournaments"][0]["id"]
    team_id = document["teams"][0]["id"]
    detail = f"/tournaments/{tournament_id}"
    address = f"{detail}/teams"
    assert address in client.get(detail).get_data(as_text=True)
    assert f'<option value="{team_id}">Águias' in client.get(address).get_data(
        as_text=True
    )
    added = client.post(address, data={"team_id": team_id})
    assert added.status_code == 302
    assert added.location == detail
    duplicate = client.post(address, data={"team_id": team_id})
    assert duplicate.status_code == 400
    assert "já está inscrita" in duplicate.get_data(as_text=True)
    assert f'<option value="{team_id}">' not in duplicate.get_data(
        as_text=True
    )

    assert (
        client.post(
            f"{address}/new",
            data={"name": "Tigres"},
        ).status_code
        == 302
    )
    summary = client.get(detail).get_data(as_text=True)
    assert "Equipes inscritas: 2" in summary
    assert "Águias" in summary and "Tigres" in summary
    assert "Remover inscrição" in summary
    assert "Inscrever novas equipes" in summary
    enrollment = client.get(address).get_data(as_text=True)
    assert "Equipes inscritas" not in enrollment
    assert "Remover inscrição" not in enrollment
    assert "Tigres" in client.get("/teams/").get_data(as_text=True)
    removed = client.post(f"{address}/{team_id}/remove")
    assert removed.status_code == 302
    assert removed.location == detail
    assert f'<option value="{team_id}">' in client.get(address).get_data(
        as_text=True
    )

    document = json.loads(path.read_text())
    registered_id = document["registrations"][0]["team_id"]
    document["tournaments"][0]["status"] = "in_progress"
    path.write_text(json.dumps(document))
    summary = client.get(detail).get_data(as_text=True)
    assert "Remover inscrição" not in summary
    assert "Inscrever novas equipes" not in summary
    assert "Inscrições encerradas" in client.get(address).get_data(
        as_text=True
    )
    assert client.post(address, data={"team_id": team_id}).status_code == 400
    assert client.post(f"{address}/{registered_id}/remove").status_code == 400
    assert client.post(f"/teams/{registered_id}/delete").status_code == 409

    document["tournaments"][0]["status"] = "draft"
    path.write_text(json.dumps(document))
    assert client.post(f"/teams/{registered_id}/delete").status_code == 302
    assert "Equipes inscritas: 0" in client.get(detail).get_data(as_text=True)
