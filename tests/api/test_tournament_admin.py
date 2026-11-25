import json

from server.app import create_app


def test_tournament_admin_flow(tmp_path):
    path = tmp_path / "data.json"
    app = create_app(path)
    with app.test_client() as client:
        response = client.post(
            "/tournaments",
            data={
                "name": "Copa São João",
                "format": "knockout",
                "modality": "Futsal",
                "start_date": "2026-11-23",
            },
        )
        assert response.status_code == 302
        document = json.loads(path.read_text())
        tournament_id = document["tournaments"][0]["id"]
        document["registrations"] = [
            {"tournament_id": tournament_id, "team_id": "a"},
            {"tournament_id": "other", "team_id": "a"},
        ]
        document["matches"] = [{"tournament_id": tournament_id}]
        document["teams"] = [{"id": "a", "name": "Águias"}]
        path.write_text(json.dumps(document))

        address = f"/tournaments/{tournament_id}"
        home = client.get("/?q=sao&status=draft").get_data(as_text=True)
        assert address in home
        assert "Futsal" in home
        assert "23/11/2026" in home
        assert "Equipes inscritas: 1" in home
        assert address not in client.get("/?status=finished").get_data(
            as_text=True
        )
        assert "Mata-mata" in client.get(address).get_data(as_text=True)
        assert client.get(f"{address}/edit").status_code == 200
        assert (
            client.post(
                f"{address}/edit",
                data={"name": "Liga", "format": "round_robin"},
            ).status_code
            == 302
        )
        assert "Liga" in client.get(address).get_data(as_text=True)
        assert client.get(f"{address}/delete").status_code == 200
        assert client.post(f"{address}/delete").status_code == 400
        assert (
            client.post(
                f"{address}/delete",
                data={"confirmed": "yes"},
            ).status_code
            == 302
        )
        assert client.get(address).status_code == 404

    document = json.loads(path.read_text())
    assert document["tournaments"] == []
    assert document["matches"] == []
    assert document["registrations"] == [
        {"tournament_id": "other", "team_id": "a"}
    ]
    assert document["teams"] == [{"id": "a", "name": "Águias"}]


def test_new_tournament_form_opens_from_list_and_keeps_invalid_input(tmp_path):
    client = create_app(tmp_path / "data.json").test_client()
    index = client.get("/").get_data(as_text=True)
    assert 'href="/tournaments/new"' in index
    assert 'name="name"' not in index

    form = client.get("/tournaments/new").get_data(as_text=True)
    assert 'action="/tournaments"' in form
    assert 'name="name"' in form

    response = client.post("/tournaments", data={"name": "Copa"})
    assert response.status_code == 400
    form = response.get_data(as_text=True)
    assert 'value="Copa"' in form
    assert "Escolha o formato do torneio." in form
