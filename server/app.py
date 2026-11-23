"""Composition root: builds the Flask application and wires dependencies.

Run from the project root with:  flask --app server.app run
"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask

from server.api.controllers.registration_controller import (
    create_registration_blueprint,
)
from server.api.controllers.team_controller import create_team_blueprint
from server.api.controllers.tournament_controller import (
    create_tournament_blueprint,
)
from server.core.use_cases.create_team import CreateTeam
from server.core.use_cases.create_tournament import CreateTournament
from server.core.use_cases.delete_tournament import DeleteTournament
from server.core.use_cases.get_tournament import GetTournament
from server.core.use_cases.update_tournament import UpdateTournament
from server.core.use_cases.delete_team import DeleteTeam
from server.core.use_cases.get_team import GetTeam
from server.core.use_cases.list_teams import ListTeams
from server.core.use_cases.list_tournaments import ListTournaments
from server.core.use_cases.tournament_registrations import TournamentRegistrations
from server.core.use_cases.update_team import UpdateTeam
from server.infrastructure.db.json_file_storage import JsonFileStorage
from server.infrastructure.db.json_team_repository import JsonTeamRepository
from server.infrastructure.db.json_tournament_repository import (
    JsonTournamentRepository,
)
from server.infrastructure.db.json_registration_repository import (
    JsonRegistrationRepository,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "instance" / "matchmanager.json"


def _new_id() -> str:
    return uuid4().hex


def create_app(data_file: Path | None = None) -> Flask:
    """Create the application, persisting data in ``data_file``."""
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "client" / "templates"),
        static_folder=str(PROJECT_ROOT / "client" / "static"),
    )

    storage = JsonFileStorage(data_file or DEFAULT_DATA_FILE)
    tournament_repository = JsonTournamentRepository(storage)
    team_repository = JsonTeamRepository(storage)

    registration_repository = JsonRegistrationRepository(storage)
    create_team = CreateTeam(team_repository, _new_id)
    get_team = GetTeam(team_repository)
    list_teams = ListTeams(team_repository)
    get_tournament = GetTournament(tournament_repository)

    registrations = TournamentRegistrations(
        registration_repository, get_tournament, get_team,
        list_teams, create_team,
    )

    app.register_blueprint(create_registration_blueprint(registrations))
    app.register_blueprint(
        create_tournament_blueprint(
            create_tournament=CreateTournament(
                repository=tournament_repository,
                id_generator=_new_id,
                clock=datetime.now,
            ),
            list_tournaments=ListTournaments(tournament_repository),
            get_tournament=get_tournament,
            registrations=registrations,
            update_tournament=UpdateTournament(tournament_repository, datetime.now),
            delete_tournament=DeleteTournament(tournament_repository),
        )
    )
    app.register_blueprint(
        create_team_blueprint(
            create_team=create_team,
            list_teams=list_teams,
            get_team=get_team,
            update_team=UpdateTeam(team_repository),
            delete_team=DeleteTeam(
                repository=team_repository,
                participation=registration_repository,
            ),
        )
    )
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
