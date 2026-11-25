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
from server.infrastructure.db.json_match_repository import JsonMatchRepository
from server.core.use_cases.configure_round_robin import ConfigureRoundRobin
from server.core.use_cases.generate_round_robin_calendar import GenerateRoundRobinCalendar
from server.core.use_cases.record_round_robin_result import RecordRoundRobinResult
from server.core.use_cases.calculate_round_robin_standings import CalculateRoundRobinStandings
from server.core.use_cases.finish_round_robin_tournament import FinishRoundRobinTournament
from server.core.use_cases.list_round_robin_matches import ListRoundRobinMatches
from server.core.use_cases.generate_knockout_bracket import (
    GenerateKnockoutBracket,
)
from server.core.use_cases.get_knockout_bracket import GetKnockoutBracket
from server.core.use_cases.start_knockout_tournament import (
    StartKnockoutTournament,
)
from server.core.use_cases.record_knockout_result import RecordKnockoutResult
from server.core.use_cases.finish_knockout_tournament import (
    FinishKnockoutTournament,
)
from server.core.use_cases.start_round_robin_tournament import (
    StartRoundRobinTournament,
)
from server.core.use_cases.start_tournament import StartTournament
from server.core.entities.tournament import TournamentFormat

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
    match_repository = JsonMatchRepository(storage)
    create_team = CreateTeam(team_repository, _new_id)
    get_team = GetTeam(team_repository)
    list_teams = ListTeams(team_repository)
    get_tournament = GetTournament(tournament_repository)
    generate_round_robin_calendar = GenerateRoundRobinCalendar(
        tournament_repository,
        registration_repository,
        match_repository,
    )
    start_knockout_tournament = StartKnockoutTournament(
        tournament_repository,
        registration_repository,
        match_repository,
    )
    start_tournament = StartTournament(
        tournament_repository,
        {
            TournamentFormat.ROUND_ROBIN: StartRoundRobinTournament(
                tournament_repository,
                generate_round_robin_calendar,
            ),
            TournamentFormat.KNOCKOUT: start_knockout_tournament,
        },
    )

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
            configure_round_robin=ConfigureRoundRobin(tournament_repository),
            generate_round_robin_calendar=generate_round_robin_calendar,
            record_round_robin_result=RecordRoundRobinResult(
                tournament_repository,
                match_repository,
            ),
            calculate_round_robin_standings=CalculateRoundRobinStandings(
                tournament_repository,
                team_repository,
                registration_repository,
                match_repository,
            ),
            finish_round_robin_tournament=FinishRoundRobinTournament(
                tournament_repository,
                match_repository,
            ),
            list_round_robin_matches=ListRoundRobinMatches(
                tournament_repository,
                match_repository,
            ),
            generate_knockout_bracket=GenerateKnockoutBracket(
                tournament_repository,
                registration_repository,
                match_repository,
                id_generator=_new_id,
            ),
            get_knockout_bracket=GetKnockoutBracket(
                tournament_repository,
                match_repository,
            ),
            start_knockout_tournament=start_knockout_tournament,
            record_knockout_result=RecordKnockoutResult(
                tournament_repository,
                match_repository,
            ),
            finish_knockout_tournament=FinishKnockoutTournament(
                tournament_repository,
                match_repository,
            ),
            start_tournament=start_tournament,
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
