from __future__ import annotations

from dataclasses import dataclass

from app.enums.organisation import OrgRole


@dataclass(frozen=True, slots=True)
class AccessContext:
    """
    Immutable, request-scoped authorization identity.

    Built exclusively from server-side authenticated state (see
    ``app.dependencies.access.get_access_context``) -- never from
    client-supplied request data. Any future retrieval/authorization
    decision that needs to know "who is asking" takes one of these rather
    than a bare ``user_id``.

    This object carries identity only. It intentionally has no methods
    (no "can_read", no "is_admin") -- authorization *policy* built on top
    of this identity belongs elsewhere; this is purely the value object.
    """

    user_id: int

    organisation_id: int

    # Deterministic, immutable, deduplicated: always a sorted tuple, never a
    # list or set. An empty tuple means "member of zero teams" -- it is
    # never treated as a wildcard by anything that reads this field.
    team_ids: tuple[int, ...]

    role: OrgRole

    def __post_init__(self) -> None:
        """
        Fail clearly rather than silently accepting an incomplete identity.

        Required fields are not ``Optional`` in the type signature, but
        Python does not enforce type hints at runtime -- a caller could
        still pass ``None`` explicitly (e.g. from a bug further up the
        dependency chain). That must never pass through unnoticed as a
        "no restriction" context, so every required field is validated
        here regardless of how it was constructed.
        """

        if not isinstance(self.user_id, int):
            raise ValueError(
                "AccessContext.user_id is required and must be an int; "
                f"got {self.user_id!r}."
            )

        if not isinstance(self.organisation_id, int):
            raise ValueError(
                "AccessContext.organisation_id is required and must be an "
                f"int; got {self.organisation_id!r}."
            )

        if not isinstance(self.role, OrgRole):
            raise ValueError(
                "AccessContext.role is required and must be an OrgRole; "
                f"got {self.role!r}."
            )

        if self.team_ids is None:
            raise ValueError(
                "AccessContext.team_ids is required; pass an empty tuple "
                "for a user with no team memberships, never None."
            )

        # Canonicalise into a deterministic, immutable, deduplicated tuple
        # regardless of what iterable the caller supplied (list, set,
        # generator, an already-sorted tuple, ...). frozen dataclasses
        # require object.__setattr__ to set a field from __post_init__.
        normalised_team_ids = tuple(sorted(set(self.team_ids)))

        if not all(isinstance(team_id, int) for team_id in normalised_team_ids):
            raise ValueError(
                "AccessContext.team_ids must contain only ints; got "
                f"{self.team_ids!r}."
            )

        object.__setattr__(self, "team_ids", normalised_team_ids)
