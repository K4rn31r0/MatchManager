"""Temporary participation query used until registrations exist."""

from server.core.interfaces.team_participation_query import (
    TeamParticipationQuery,
)


class NoRegistrationsParticipationQuery(TeamParticipationQuery):
    """Answers that no team plays a started tournament.

    Team registrations are introduced by issue 04; until then no team can
    belong to a tournament, so this is the correct answer. Issue 04 replaces
    this class with a query backed by the persisted registrations.
    """

    def is_in_started_tournament(self, team_id: str) -> bool:
        return False
