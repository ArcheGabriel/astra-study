from enum import Enum


class OrgRole(str, Enum):
    """
    A user's organisation-scoped role.

    Distinct from document access scope -- role governs capabilities
    (who may create an ORGANISATION-scoped document, manage teams, manage
    member roles), never document visibility.
    """

    MEMBER = "member"

    MANAGER = "manager"

    ADMIN = "admin"
