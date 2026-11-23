"""Composition root: builds the Flask application and wires dependencies.

Run from the project root with:  flask --app server.app run
"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask

from server.api.controllers.tournament_controller import (
    create_tournament_blueprint,
)
from server.core.use_cases.create_tournament import CreateTournament
from server.core.use_cases.list_tournaments import ListTournaments
from server.infrastructure.db.json_file_storage import JsonFileStorage
from server.infrastructure.db.json_tournament_repository import (
    JsonTournamentRepository,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "instance" / "matchmanager.json"


def create_app(data_file: Path | None = None) -> Flask:
    """Create the application, persisting data in ``data_file``."""
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "client" / "templates"),
        static_folder=str(PROJECT_ROOT / "client" / "static"),
    )

    storage = JsonFileStorage(data_file or DEFAULT_DATA_FILE)
    tournament_repository = JsonTournamentRepository(storage)

    app.register_blueprint(
        create_tournament_blueprint(
            create_tournament=CreateTournament(
                repository=tournament_repository,
                id_generator=lambda: uuid4().hex,
                clock=datetime.now,
            ),
            list_tournaments=ListTournaments(tournament_repository),
        )
    )
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
