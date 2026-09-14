from enum import Enum


class TeamRole(str, Enum):
    """
    A user's role within a single team membership.

    Independent of ``OrgRole``: a user can be a MANAGER of one team and a
    plain MEMBER of another.
    """

    MEMBER = "member"

    MANAGER = "manager"
