"""HTTP routes for tournaments."""

from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.datastructures import MultiDict

from server.api.presenters.team_presenter import present_teams
from server.api.presenters.tournament_presenter import (
    FORMAT_LABELS,
    STATUS_LABELS,
    present_tournament,
    present_tournaments,
)
from server.core.entities.tournament import TournamentFormat, TournamentStatus
from server.core.errors import DomainError, TournamentNotFoundError
from server.core.use_cases.create_tournament import (
    CreateTournament,
    CreateTournamentInput,
)
from server.core.use_cases.delete_tournament import DeleteTournament
from server.core.use_cases.get_tournament import GetTournament
from server.core.use_cases.update_tournament import UpdateTournament
from server.core.use_cases.list_tournaments import ListTournaments
from server.core.use_cases.tournament_registrations import TournamentRegistrations


class InvalidFormError(Exception):
    """The submitted form cannot be converted into use case input."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def create_tournament_blueprint(
    create_tournament: CreateTournament,
    list_tournaments: ListTournaments,
    get_tournament: GetTournament,
    registrations: TournamentRegistrations,
    update_tournament: UpdateTournament,
    delete_tournament: DeleteTournament,
) -> Blueprint:
    """Build the tournament routes around the injected use cases."""
    blueprint = Blueprint("tournaments", __name__)

    @blueprint.errorhandler(TournamentNotFoundError)
    def not_found(error: TournamentNotFoundError):
        return render_template("not_found.html", message=error.message), 404

    @blueprint.get("/")
    def index() -> str:
        search = request.args.get("q", "")
        status_value = request.args.get("status", "")
        status = next(
            (item for item in TournamentStatus if item.value == status_value),
            None,
        )
        order = request.args.get("order", "activity")
        return render_template(
            "tournaments/index.html",
            search=search,
            status=status_value,
            status_options=STATUS_LABELS,
            order=order,
            tournaments=present_tournaments(
                list_tournaments.execute(search, status, order),
                list_tournaments.participant_counts(),
            ),
        )

    def render_new(
        form: MultiDict[str, str] | None = None,
        error: str | None = None,
    ) -> str:
        return render_template(
            "tournaments/new.html",
            format_options=FORMAT_LABELS,
            form=form if form is not None else MultiDict(),
            error=error,
        )

    @blueprint.get("/tournaments/new")
    def new() -> str:
        return render_new()

    @blueprint.post("/tournaments")
    def create():
        try:
            create_tournament.execute(_parse_create_form(request.form))
        except (InvalidFormError, DomainError) as error:
            return render_new(form=request.form, error=error.message), 400
        return redirect(url_for("tournaments.index"))

    def render_detail(tournament_id: str, error: str | None = None) -> str:
        teams = registrations.list(tournament_id)
        return render_template(
            "tournaments/detail.html",
            tournament=present_tournament(teams.tournament, len(teams.registered)),
            registered=present_teams(teams.registered),
            error=error,
        )

    @blueprint.get("/tournaments/<tournament_id>")
    def detail(tournament_id: str) -> str:
        return render_detail(tournament_id)

    @blueprint.post("/tournaments/<tournament_id>/teams/<team_id>/remove")
    def remove_registration(tournament_id: str, team_id: str):
        try:
            registrations.remove(tournament_id, team_id)
        except TournamentNotFoundError:
            raise
        except DomainError as error:
            return render_detail(tournament_id, error.message), 400
        return redirect(url_for(".detail", tournament_id=tournament_id))

    @blueprint.route("/tournaments/<tournament_id>/edit", methods=["GET", "POST"])
    def edit(tournament_id: str):
        tournament = get_tournament.execute(tournament_id)
        form = {
            "name": tournament.name,
            "format": tournament.tournament_format.value,
            "modality": tournament.modality or "",
            "start_date": tournament.start_date or "",
            "end_date": tournament.end_date or "",
        }
        error = None
        if request.method == "POST":
            form = request.form
            try:
                update_tournament.execute(tournament_id, _parse_create_form(form))
            except (InvalidFormError, DomainError) as failure:
                error = failure.message
            else:
                return redirect(url_for(".detail", tournament_id=tournament_id))
        return render_template(
            "tournaments/edit.html", tournament=present_tournament(tournament),
            form=form, format_options=FORMAT_LABELS, error=error,
        ), 400 if error else 200

    @blueprint.route("/tournaments/<tournament_id>/delete", methods=["GET", "POST"])
    def delete(tournament_id: str):
        tournament = get_tournament.execute(tournament_id)
        error = None
        if request.method == "POST":
            try:
                delete_tournament.execute(
                    tournament_id, confirmed=request.form.get("confirmed") == "yes",
                )
            except DomainError as failure:
                error = failure.message
            else:
                return redirect(url_for(".index"))
        return render_template(
            "tournaments/delete.html", tournament=present_tournament(tournament),
            error=error,
        ), 400 if error else 200

    return blueprint


def _parse_create_form(form: MultiDict[str, str]) -> CreateTournamentInput:
    return CreateTournamentInput(
        name=form.get("name", ""),
        tournament_format=_parse_format(form.get("format", "")),
        modality=form.get("modality"),
        start_date=_parse_date(form.get("start_date", ""), "início"),
        end_date=_parse_date(form.get("end_date", ""), "término"),
    )


def _parse_format(value: str) -> TournamentFormat:
    try:
        return TournamentFormat(value)
    except ValueError:
        raise InvalidFormError("Escolha o formato do torneio.") from None


def _parse_date(value: str, label: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise InvalidFormError(f"Data de {label} inválida.") from None
