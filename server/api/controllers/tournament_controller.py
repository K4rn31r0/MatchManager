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
from server.core.entities.team import Team
from server.core.entities.tournament import (
    KnockoutByeStrategy,
    KnockoutOrderMode,
    RoundRobinMode,
    TournamentFormat,
    TournamentStatus,
)
from server.core.entities.match import MatchResult
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
from server.core.use_cases.configure_round_robin import (
    ConfigureRoundRobin,
    RoundRobinConfigInput,
)
from server.core.use_cases.generate_round_robin_calendar import (
    GenerateRoundRobinCalendar,
)
from server.core.use_cases.record_round_robin_result import (
    RecordRoundRobinResult,
    RoundRobinResultInput,
)
from server.core.use_cases.calculate_round_robin_standings import (
    CalculateRoundRobinStandings,
)
from server.core.use_cases.finish_round_robin_tournament import (
    FinishRoundRobinTournament,
)
from server.core.use_cases.list_round_robin_matches import (
    ListRoundRobinMatches,
)
from server.core.use_cases.generate_knockout_bracket import (
    GenerateKnockoutBracket,
    KnockoutBracketInput,
)
from server.core.use_cases.get_knockout_bracket import GetKnockoutBracket
from server.core.use_cases.start_knockout_tournament import (
    StartKnockoutTournament,
)


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
    configure_round_robin: ConfigureRoundRobin,
    generate_round_robin_calendar: GenerateRoundRobinCalendar,
    record_round_robin_result: RecordRoundRobinResult,
    calculate_round_robin_standings: CalculateRoundRobinStandings,
    finish_round_robin_tournament: FinishRoundRobinTournament,
    list_round_robin_matches: ListRoundRobinMatches,
    generate_knockout_bracket: GenerateKnockoutBracket,
    get_knockout_bracket: GetKnockoutBracket,
    start_knockout_tournament: StartKnockoutTournament,
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

    def render_detail(
        tournament_id: str,
        error: str | None = None,
        form: MultiDict[str, str] | None = None,
    ) -> str:
        teams = registrations.list(tournament_id)
        matches = []
        standings = None
        champion_team_id = None
        knockout_bracket = None
        knockout_bye_count = 0
        if teams.tournament.tournament_format is TournamentFormat.ROUND_ROBIN:
            try:
                matches = list_round_robin_matches.execute(tournament_id)
                standings = calculate_round_robin_standings.execute(tournament_id)
                champion_team_id = standings.champion_team_id
            except DomainError:
                matches = []
                standings = None
        else:
            knockout_bracket = get_knockout_bracket.execute(tournament_id)
            participant_count = len(teams.registered)
            if participant_count >= 2:
                bracket_size = 1 << (participant_count - 1).bit_length()
                knockout_bye_count = bracket_size - participant_count
        registered_ids = [team.id for team in teams.registered]
        knockout_config = teams.tournament.knockout
        team_order = registered_ids
        if knockout_config is not None:
            order_has_all_teams = (
                len(knockout_config.initial_order) == len(registered_ids)
            )
            order_uses_registered_teams = (
                set(knockout_config.initial_order) == set(registered_ids)
            )
            if order_has_all_teams and order_uses_registered_teams:
                team_order = knockout_config.initial_order
        return render_template(
            "tournaments/detail.html",
            tournament=present_tournament(teams.tournament, len(teams.registered)),
            registered=present_teams(teams.registered),
            matches=matches,
            standings=standings,
            champion_team_id=champion_team_id,
            knockout_bracket=knockout_bracket,
            knockout_bye_count=knockout_bye_count,
            team_names={team.id: team.name for team in teams.registered},
            team_positions={
                team_id: position
                for position, team_id in enumerate(team_order, start=1)
            },
            error=error,
            form=form or MultiDict(),
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

    @blueprint.post("/tournaments/<tournament_id>/round-robin/configure")
    def configure_round_robin_route(tournament_id: str):
        try:
            names = request.form.getlist("tie_breaker_name")
            directions = request.form.getlist("tie_breaker_direction")
            tie_breakers = tuple(
                (name, direction)
                for name, direction in zip(names, directions)
                if name.strip()
            )
            configured = configure_round_robin.execute(
                tournament_id,
                RoundRobinConfigInput(
                    mode=RoundRobinMode(request.form["mode"]),
                    win_points=_parse_points(request.form, "win_points", 3),
                    draw_points=_parse_points(request.form, "draw_points", 1),
                    loss_points=_parse_points(request.form, "loss_points", 0),
                    tie_breakers=tie_breakers,
                    statistic_fields=tuple(
                        item.strip()
                        for item in request.form.get("statistic_fields", "").split(",")
                        if item.strip()
                    ),
                ),
            )
        except (KeyError, ValueError, InvalidFormError, DomainError) as error:
            message = (
                error.message if isinstance(error, DomainError)
                else "Informe uma configuração válida."
            )
            return render_detail(tournament_id, message), 400
        return redirect(url_for(".detail", tournament_id=tournament_id))

    @blueprint.post("/tournaments/<tournament_id>/round-robin/generate")
    def generate_round_robin_calendar_route(tournament_id: str):
        try:
            generate_round_robin_calendar.execute(tournament_id)
        except DomainError as error:
            return render_detail(tournament_id, error.message), 400
        return redirect(url_for(".detail", tournament_id=tournament_id))

    @blueprint.post("/tournaments/<tournament_id>/knockout/generate")
    def generate_knockout_bracket_route(tournament_id: str):
        try:
            teams = registrations.list(tournament_id)
            data = _parse_knockout_form(request.form, teams.registered)
            generate_knockout_bracket.execute(tournament_id, data)
        except (InvalidFormError, ValueError, DomainError) as error:
            message = (
                error.message if isinstance(error, DomainError)
                else (
                    error.message
                    if isinstance(error, InvalidFormError)
                    else "Informe uma configuração de chaveamento válida."
                )
            )
            return render_detail(tournament_id, message, request.form), 400
        return redirect(url_for(".detail", tournament_id=tournament_id))

    @blueprint.post("/tournaments/<tournament_id>/knockout/start")
    def start_knockout_tournament_route(tournament_id: str):
        try:
            start_knockout_tournament.execute(tournament_id)
        except DomainError as error:
            return render_detail(tournament_id, error.message), 400
        return redirect(url_for(".detail", tournament_id=tournament_id))

    @blueprint.post("/tournaments/<tournament_id>/matches/<match_id>/result")
    def record_round_robin_result_route(tournament_id: str, match_id: str):
        try:
            tournament = get_tournament.execute(tournament_id)
            result_value = request.form.get("result", "")
            if not result_value:
                raise InvalidFormError("Informe vitória, empate ou derrota.")
            result = MatchResult(result_value)
            first_score = _parse_optional_score(request.form, "first_score")
            second_score = _parse_optional_score(request.form, "second_score")
            first_stats = _parse_match_stats(request.form, "first")
            second_stats = _parse_match_stats(request.form, "second")
            record_round_robin_result.execute(
                tournament_id,
                match_id,
                RoundRobinResultInput(
                    result=result,
                    first_score=first_score,
                    second_score=second_score,
                    first_team_stats=first_stats,
                    second_team_stats=second_stats,
                ),
            )
        except (InvalidFormError, ValueError, DomainError) as error:
            message = (
                error.message if isinstance(error, DomainError)
                else (
                    error.message
                    if isinstance(error, InvalidFormError)
                    else "Informe um resultado válido."
                )
            )
            return render_detail(tournament_id, message), 400
        return redirect(url_for(".detail", tournament_id=tournament_id))

    @blueprint.post("/tournaments/<tournament_id>/round-robin/finish")
    def finish_round_robin_tournament_route(tournament_id: str):
        try:
            finish_round_robin_tournament.execute(tournament_id)
        except DomainError as error:
            return render_detail(tournament_id, error.message), 400
        return redirect(url_for(".detail", tournament_id=tournament_id))

    return blueprint


def _parse_create_form(form: MultiDict[str, str]) -> CreateTournamentInput:
    return CreateTournamentInput(
        name=form.get("name", ""),
        tournament_format=_parse_format(form.get("format", "")),
        modality=form.get("modality"),
        start_date=_parse_date(form.get("start_date", ""), "início"),
        end_date=_parse_date(form.get("end_date", ""), "término"),
    )


def _parse_knockout_form(
    form: MultiDict[str, str],
    registered: list[Team],
) -> KnockoutBracketInput:
    try:
        order_mode = KnockoutOrderMode(form.get("order_mode", ""))
        bye_strategy = KnockoutByeStrategy(form.get("bye_strategy", ""))
    except ValueError:
        raise InvalidFormError(
            "Escolha a ordem inicial e a estratégia de bye."
        ) from None

    order: tuple[str, ...] = ()
    if order_mode is KnockoutOrderMode.MANUAL:
        positions: list[tuple[int, str]] = []
        try:
            positions = [
                (int(form.get(f"team_order_{team.id}", "")), team.id)
                for team in registered
            ]
        except ValueError:
            raise InvalidFormError(
                "Informe uma posição manual para cada equipe."
            ) from None
        position_values = [position for position, _ in positions]
        has_non_positive_position = any(
            position < 1 for position in position_values
        )
        has_duplicate_positions = (
            len(set(position_values)) != len(position_values)
        )
        if has_non_positive_position or has_duplicate_positions:
            raise InvalidFormError(
                "Cada equipe precisa ter uma posição manual única."
            )
        order = tuple(
            team_id for _, team_id in sorted(positions)
        )
    return KnockoutBracketInput(
        order_mode=order_mode,
        initial_order=order,
        bye_strategy=bye_strategy,
        bye_team_ids=tuple(form.getlist("bye_team_ids")),
    )


def _parse_format(value: str) -> TournamentFormat:
    try:
        return TournamentFormat(value)
    except ValueError:
        raise InvalidFormError("Escolha o formato do torneio.") from None


def _parse_points(
    form: MultiDict[str, str],
    name: str,
    default: int,
) -> int:
    value = form.get(name, "")
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise InvalidFormError("A pontuação deve ser numérica.") from None


def _parse_optional_score(
    form: MultiDict[str, str],
    name: str,
) -> int | None:
    value = form.get(name, "").strip()
    if not value:
        return None
    try:
        score = int(value)
    except ValueError:
        raise InvalidFormError("O placar deve usar números.") from None
    if score < 0:
        raise InvalidFormError("O placar não pode ser negativo.")
    return score


def _parse_match_stats(
    form: MultiDict[str, str],
    side: str,
) -> dict[str, int] | None:
    prefix = f"{side}_stat_"
    values: dict[str, int] = {}
    for name, value in form.items(multi=False):
        if not name.startswith(prefix) or not value.strip():
            continue
        try:
            values[name[len(prefix):]] = int(value)
        except ValueError:
            raise InvalidFormError("As estatísticas devem ser numéricas.") from None
    return values or None


def _parse_date(value: str, label: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise InvalidFormError(f"Data de {label} inválida.") from None
