import json

from server.app import create_app


def test_round_robin_result_form_rejects_partial_and_persists_complete_score(
    tmp_path,
):
    path = tmp_path / "data.json"
    app = create_app(path)
    client = app.test_client()
    tournament_id = "t1"
    document = {
        "tournaments": [
            {
                "id": tournament_id,
                "name": "Liga",
                "format": "round_robin",
                "status": "in_progress",
                "created_at": "2026-11-23T12:00:00",
                "round_robin": {
                    "mode": "single",
                    "win_points": 3,
                    "draw_points": 1,
                    "loss_points": 0,
                    "tie_breakers": [
                        {"name": "Saldo", "direction": "positive"}
                    ],
                    "statistic_fields": ["Gols"],
                },
            }
        ],
        "teams": [
            {"id": "a", "name": "Águias", "abbreviation": "AGU"},
            {"id": "b", "name": "Tigres", "abbreviation": "TIG"},
        ],
        "registrations": [
            {"tournament_id": tournament_id, "team_id": "a"},
            {"tournament_id": tournament_id, "team_id": "b"},
        ],
        "matches": [
            {
                "id": "m1",
                "tournament_id": tournament_id,
                "round": 1,
                "first_team_id": "a",
                "second_team_id": "b",
                "status": "pending",
            }
        ],
    }
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")

    address = f"/tournaments/{tournament_id}/matches/m1/result"
    partial = client.post(
        address,
        data={
            "result": "first_win",
            "first_score": "2",
            "second_score": "",
        },
    )
    assert partial.status_code == 400
    assert "placar completo" in partial.get_data(as_text=True)

    complete = client.post(
        address,
        data={
            "result": "first_win",
            "first_score": "2",
            "second_score": "1",
            "first_stat_Gols": "2",
            "second_stat_Gols": "1",
        },
    )
    assert complete.status_code == 302

    saved = json.loads(path.read_text(encoding="utf-8"))
    match = saved["matches"][0]
    assert match["status"] == "completed"
    assert match["result"] == "first_win"
    assert match["first_score"] == 2
    assert match["second_score"] == 1
    assert match["first_team_stats"]["Gols"] == 2
