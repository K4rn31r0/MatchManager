"""Use cases for viewing and changing a tournament's registrations."""

from dataclasses import dataclass

from server.core.entities.team import Team
from server.core.entities.tournament import Tournament
from server.core.errors import DomainError
from server.core.interfaces.registration_repository import RegistrationRepository
from server.core.use_cases.create_team import CreateTeam
from server.core.use_cases.get_team import GetTeam
from server.core.use_cases.get_tournament import GetTournament
from server.core.use_cases.list_teams import ListTeams
from server.core.use_cases.team_data import TeamData


@dataclass(frozen=True)
class TournamentTeams:
    tournament: Tournament
    registered: list[Team]
    available: list[Team]


class TournamentRegistrations:
    """Coordinates operations on the participant list of one tournament."""

    def __init__(
        self,
        registrations: RegistrationRepository,
        get_tournament: GetTournament,
        get_team: GetTeam,
        list_teams: ListTeams,
        create_team: CreateTeam,
    ) -> None:
        self._registrations = registrations
        self._get_tournament = get_tournament
        self._get_team = get_team
        self._list_teams = list_teams
        self._create_team = create_team

    def list(self, tournament_id: str) -> TournamentTeams:
        tournament = self._get_tournament.execute(tournament_id)
        registered_ids = self._registrations.team_ids(tournament_id)
        teams = self._list_teams.execute()
        return TournamentTeams(
            tournament=tournament,
            registered=[team for team in teams if team.id in registered_ids],
            available=[team for team in teams if team.id not in registered_ids],
        )

    def add(self, tournament_id: str, team_id: str) -> None:
        self._get_tournament.execute(tournament_id).ensure_registrations_open()
        team = self._get_team.execute(team_id)
        if team.id in self._registrations.team_ids(tournament_id):
            raise DomainError("Esta equipe já está inscrita neste torneio.")
        self._registrations.add(tournament_id, team.id)

    def create_and_add(self, tournament_id: str, data: TeamData) -> Team:
        self._get_tournament.execute(tournament_id).ensure_registrations_open()
        team = self._create_team.prepare(data)
        self._registrations.add_new_team(tournament_id, team)
        return team

    def remove(self, tournament_id: str, team_id: str) -> None:
        self._get_tournament.execute(tournament_id).ensure_registrations_open()
        if team_id not in self._registrations.team_ids(tournament_id):
            raise DomainError("Esta equipe não está inscrita neste torneio.")
        self._registrations.remove(tournament_id, team_id)
