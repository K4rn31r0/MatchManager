"""Query contract about the tournaments a team takes part in."""

from abc import ABC, abstractmethod


class TeamParticipationQuery(ABC):
    """Answers questions about a team's tournament registrations."""

    @abstractmethod
    def is_in_started_tournament(self, team_id: str) -> bool:
        """Tell whether the team plays a tournament that has started.

        A tournament has started when it is in progress or finished.
        """
