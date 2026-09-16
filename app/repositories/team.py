from sqlalchemy.orm import Session

from app.models.team import Team
from app.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    """
    Repository for Team database operations.

    Deliberately minimal: document creation only needs to resolve a
    client-supplied ``team_id`` to its owning organisation, which
    ``get_by_id`` (inherited from ``BaseRepository``) already provides.
    Team management (create/rename/delete) is out of scope -- see
    RBAC-5E's investigation report.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        super().__init__(
            db=db,
            model=Team,
        )
