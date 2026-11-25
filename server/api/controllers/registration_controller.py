"""HTTP routes for a tournament's registrations."""

from collections.abc import Mapping

from flask import Blueprint, redirect, render_template, request, url_for

from server.api.controllers.team_form import parse_team_form
from server.api.presenters.team_presenter import present_teams
from server.api.presenters.tournament_presenter import present_tournament
from server.core.errors import DomainError, TournamentNotFoundError
from server.core.use_cases.tournament_registrations import (
    TournamentRegistrations,
)


def create_registration_blueprint(
    use_cases: TournamentRegistrations,
) -> Blueprint:
    blueprint = Blueprint(
        "registrations",
        __name__,
        url_prefix="/tournaments/<tournament_id>/teams",
    )

    @blueprint.errorhandler(TournamentNotFoundError)
    def not_found(error: TournamentNotFoundError) -> tuple[str, int]:
        return render_template("not_found.html", message=error.message), 404

    def render_teams(
        tournament_id: str,
        error: str | None = None,
        form: Mapping[str, str] | None = None,
    ) -> str:
        teams = use_cases.list(tournament_id)
        return render_template(
            "tournaments/teams.html",
            tournament=present_tournament(teams.tournament),
            available=present_teams(teams.available),
            form=form or {},
            error=error,
        )

    @blueprint.get("")
    def index(tournament_id: str) -> str:
        return render_teams(tournament_id)

    @blueprint.post("")
    def add(tournament_id: str):
        try:
            use_cases.add(tournament_id, request.form.get("team_id", ""))
        except TournamentNotFoundError:
            raise
        except DomainError as error:
            return render_teams(tournament_id, error.message), 400
        return redirect(
            url_for("tournaments.detail", tournament_id=tournament_id)
        )

    @blueprint.post("/new")
    def create(tournament_id: str):
        try:
            use_cases.create_and_add(
                tournament_id, parse_team_form(request.form)
            )
        except TournamentNotFoundError:
            raise
        except DomainError as error:
            return render_teams(
                tournament_id, error.message, request.form
            ), 400
        return redirect(
            url_for("tournaments.detail", tournament_id=tournament_id)
        )

    return blueprint
