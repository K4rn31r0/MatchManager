"""HTTP routes for tournaments."""

from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.datastructures import MultiDict

from server.api.presenters.tournament_presenter import (
    FORMAT_LABELS,
    present_tournaments,
)
from server.core.entities.tournament import TournamentFormat
from server.core.errors import DomainError
from server.core.use_cases.create_tournament import (
    CreateTournament,
    CreateTournamentInput,
)
from server.core.use_cases.list_tournaments import ListTournaments


class InvalidFormError(Exception):
    """The submitted form cannot be converted into use case input."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def create_tournament_blueprint(
    create_tournament: CreateTournament,
    list_tournaments: ListTournaments,
) -> Blueprint:
    """Build the tournament routes around the injected use cases."""
    blueprint = Blueprint("tournaments", __name__)

    def render_index(
        form: MultiDict[str, str] | None = None,
        error: str | None = None,
    ) -> str:
        return render_template(
            "tournaments/index.html",
            tournaments=present_tournaments(list_tournaments.execute()),
            format_options=FORMAT_LABELS,
            form=form or MultiDict(),
            error=error,
        )

    @blueprint.get("/")
    def index() -> str:
        return render_index()

    @blueprint.post("/tournaments")
    def create():
        try:
            create_tournament.execute(_parse_create_form(request.form))
        except (InvalidFormError, DomainError) as error:
            return render_index(form=request.form, error=error.message), 400
        return redirect(url_for("tournaments.index"))

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
