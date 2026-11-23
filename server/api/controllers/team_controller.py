"""HTTP routes for teams."""

from collections.abc import Mapping

from flask import Blueprint, redirect, render_template, request, url_for

from server.api.controllers.team_form import parse_team_form
from server.api.presenters.team_presenter import (
    present_team,
    present_teams,
    team_form_values,
)
from server.core.errors import DomainError, TeamNotFoundError
from server.core.use_cases.create_team import CreateTeam
from server.core.use_cases.delete_team import DeleteTeam
from server.core.use_cases.get_team import GetTeam
from server.core.use_cases.list_teams import ListTeams
from server.core.use_cases.update_team import UpdateTeam

_NEW_TEAM_FORM = {"color": "#1f6feb"}


def create_team_blueprint(
    create_team: CreateTeam,
    list_teams: ListTeams,
    get_team: GetTeam,
    update_team: UpdateTeam,
    delete_team: DeleteTeam,
) -> Blueprint:
    """Build the team routes around the injected use cases."""
    blueprint = Blueprint("teams", __name__, url_prefix="/teams")

    @blueprint.errorhandler(TeamNotFoundError)
    def team_not_found(error: TeamNotFoundError):
        return render_template("not_found.html", message=error.message), 404

    def render_index(
        form: Mapping[str, str] = _NEW_TEAM_FORM, error: str | None = None
    ) -> str:
        search = request.args.get("q", "")
        return render_template(
            "teams/index.html",
            teams=present_teams(list_teams.execute(search)),
            search=search,
            form=form,
            error=error,
        )

    @blueprint.get("/")
    def index() -> str:
        return render_index()

    @blueprint.post("/")
    def create():
        try:
            create_team.execute(parse_team_form(request.form))
        except DomainError as error:
            return render_index(form=request.form, error=error.message), 400
        return redirect(url_for("teams.index"))

    @blueprint.get("/<team_id>")
    def detail(team_id: str) -> str:
        return render_template(
            "teams/detail.html", team=present_team(get_team.execute(team_id))
        )

    @blueprint.get("/<team_id>/edit")
    def edit(team_id: str) -> str:
        team = get_team.execute(team_id)
        return render_template(
            "teams/edit.html",
            team=present_team(team),
            form=team_form_values(team),
            error=None,
        )

    @blueprint.post("/<team_id>/edit")
    def update(team_id: str):
        try:
            update_team.execute(team_id, parse_team_form(request.form))
        except TeamNotFoundError:
            raise
        except DomainError as error:
            team = present_team(get_team.execute(team_id))
            return (
                render_template(
                    "teams/edit.html",
                    team=team,
                    form=request.form,
                    error=error.message,
                ),
                400,
            )
        return redirect(url_for("teams.detail", team_id=team_id))

    @blueprint.get("/<team_id>/delete")
    def confirm_delete(team_id: str) -> str:
        return render_template(
            "teams/delete.html",
            team=present_team(get_team.execute(team_id)),
            error=None,
        )

    @blueprint.post("/<team_id>/delete")
    def delete(team_id: str):
        try:
            delete_team.execute(team_id)
        except TeamNotFoundError:
            raise
        except DomainError as error:
            team = present_team(get_team.execute(team_id))
            return (
                render_template(
                    "teams/delete.html", team=team, error=error.message
                ),
                409,
            )
        return redirect(url_for("teams.index"))

    return blueprint
