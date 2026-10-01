from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.user import RoleManagementSearchResult


class RoleManagementService:
    """
    Service responsible for organisation role administration (RBAC
    Phase C.2): searching organisation users with their current
    ``OrgRole``, and promoting a user's role.

    Deliberately separate from ``frontend.api.user_service.UserService``
    (team-membership search only, never exposes ``role``) and from
    ``OrgManagerService`` (Org Manager jurisdiction, a structurally
    independent concept) -- mirrors the backend's own split between
    ``UserService.search_organisation_users`` /
    ``search_organisation_users_with_role`` / ``update_role``. The
    backend remains the sole authority for every operation here -- this
    service performs no authorization of its own.
    """

    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    def search_users(
        self,
        query: str,
    ) -> list[RoleManagementSearchResult]:
        """
        Search for users within the requester's own organisation,
        including their current ``OrgRole``.

        ADMIN-only on the backend -- a non-ADMIN caller receives an
        ``ApiException`` from a 403 response.
        """

        data = self.client.get(
            "/users/role-management",
            params={
                "q": query,
            },
        )

        return [
            RoleManagementSearchResult.from_dict(item)
            for item in data
        ]

    def update_role(
        self,
        user_id: int,
        role: str,
    ) -> None:
        """
        Change ``user_id``'s organisation role.

        Only ``MEMBER -> MANAGER`` and ``MANAGER -> ADMIN`` are
        permitted -- the backend remains authoritative about which
        transitions, if any, are allowed; this call does no eligibility
        pre-check and does no self-modification guard of its own.

        Returns ``None`` -- the backend response (``RoleManagementUserResponse``:
        ``id``/``username``/``role``, no ``email``) is a different, thinner
        shape than ``RoleManagementSearchResult`` and is deliberately not
        parsed here. Callers must re-fetch (``search_users``) to see the
        new state, mirroring ``OrgManagerService.grant``/``revoke``'s
        identical "never trust a mutation's own response, always
        re-fetch" precedent -- this is also what the UI is required to
        do (no optimistic local mutation).
        """

        self.client.post(
            f"/users/{user_id}/role",
            json={
                "role": role,
            },
        )
