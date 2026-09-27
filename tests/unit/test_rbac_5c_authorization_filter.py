"""
Executable specification for RBAC-5C: server-side document-visibility
authorization in the production Qdrant retrieval filter.

Covers, with no live Qdrant connection (``DenseRepository.__new__`` with a
mocked ``client``, matching the pattern already established in
``tests/unit/test_rbac_5b_propagation.py``):

- INDIVIDUAL branch: owner-only, with an explicit ``IsEmptyCondition``
  accommodation for legacy (schema_version=2) points that never wrote an
  ``access_scope`` field at all;
- TEAM branch: only constructed for non-empty ``access.team_ids``, always
  requires organisation match, never constructs ``MatchAny(any=[])``;
- ORGANISATION branch: only constructed for ``OrgRole.ADMIN``, role is
  never encoded as a Qdrant filter condition;
- structural filters (``is_reference``/``is_appendix``) remain unconditional;
- legacy v2 points can never gain TEAM/ORGANISATION visibility;
- the same filter object is reused for both the dense and sparse
  ``Prefetch`` branches (unchanged RRF behaviour).
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from qdrant_client.models import Filter, IsEmptyCondition, MatchAny, MatchValue

from app.enums.organisation import OrgRole
from app.retrieval.access import AccessContext
from app.search.dense.repository import DenseRepository


def make_access(
    *,
    user_id: int = 1,
    organisation_id: int = 1,
    team_ids: tuple[int, ...] = (),
    jurisdiction_team_ids: tuple[int, ...] = (),
    role: OrgRole = OrgRole.MEMBER,
) -> AccessContext:
    return AccessContext(
        user_id=user_id,
        organisation_id=organisation_id,
        team_ids=team_ids,
        jurisdiction_team_ids=jurisdiction_team_ids,
        role=role,
    )


def make_dense_repository_with_fake_client() -> DenseRepository:
    repository = DenseRepository.__new__(DenseRepository)
    repository.client = MagicMock()
    repository.client.query_points.return_value = SimpleNamespace(points=[])
    return repository


def call_hybrid_search(repository: DenseRepository, access: AccessContext):
    repository.hybrid_search(
        dense_vector=[0.1],
        sparse_indices=[1],
        sparse_values=[0.5],
        access=access,
        limit=5,
    )
    call = repository.client.query_points.call_args
    dense_prefetch, sparse_prefetch = call.kwargs["prefetch"]
    return dense_prefetch.filter, sparse_prefetch.filter


def branch_filter(retrieval_filter: Filter) -> Filter:
    """The nested Filter(should=[...]) appended after the structural conditions."""

    nested = [c for c in retrieval_filter.must if isinstance(c, Filter)]
    assert len(nested) == 1
    return nested[0]


def find_matchany(node) -> list[MatchAny]:
    """Recursively collect every MatchAny instance anywhere in a Filter tree."""

    found: list[MatchAny] = []

    def walk(value):
        if isinstance(value, MatchAny):
            found.append(value)
        elif isinstance(value, Filter):
            for group in (value.must, value.should, value.must_not):
                if group is None:
                    continue
                items = group if isinstance(group, list) else [group]
                for item in items:
                    walk(item)
        elif hasattr(value, "match"):
            walk(value.match)

    walk(node)
    return found


# --------------------------------------------------------------------------- #
# A. Individual
# --------------------------------------------------------------------------- #


def test_individual_branch_requires_own_user_id():
    repository = make_dense_repository_with_fake_client()
    access = make_access(user_id=7)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branches = branch_filter(retrieval_filter)

    individual = branches.should[0]
    assert isinstance(individual, Filter)
    user_id_conditions = [c.match.value for c in individual.must if c.key == "user_id"]
    assert user_id_conditions == [7]


def test_individual_branch_different_user_id_produces_different_condition():
    repository = make_dense_repository_with_fake_client()

    filter_a, _ = call_hybrid_search(repository, make_access(user_id=1))
    filter_b, _ = call_hybrid_search(repository, make_access(user_id=999))

    individual_a = branch_filter(filter_a).should[0]
    individual_b = branch_filter(filter_b).should[0]

    value_a = [c.match.value for c in individual_a.must if c.key == "user_id"][0]
    value_b = [c.match.value for c in individual_b.must if c.key == "user_id"][0]
    assert value_a != value_b


# --------------------------------------------------------------------------- #
# B. Team
# --------------------------------------------------------------------------- #


def test_team_branch_exists_for_non_empty_team_ids():
    repository = make_dense_repository_with_fake_client()
    access = make_access(team_ids=(10, 11))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branches = branch_filter(retrieval_filter).should

    team_branches = [
        b for b in branches
        if isinstance(b, Filter)
        and any(c.key == "access_scope" and c.match.value == "team" for c in b.must)
    ]
    assert len(team_branches) == 1


def test_team_branch_does_not_require_user_id():
    """Team-shared documents must be visible to any team member, not gated
    by individual ownership -- the TEAM branch must never carry a user_id
    condition (that would collapse team sharing back into individual-only
    access)."""

    repository = make_dense_repository_with_fake_client()
    access = make_access(team_ids=(10, 11))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branches = branch_filter(retrieval_filter).should
    team_branch = next(
        b for b in branches
        if isinstance(b, Filter)
        and any(c.key == "access_scope" and c.match.value == "team" for c in b.must)
    )

    keys = {c.key for c in team_branch.must}
    assert "user_id" not in keys


def test_team_branch_matchany_contains_supplied_team_ids():
    repository = make_dense_repository_with_fake_client()
    access = make_access(team_ids=(3, 1, 2))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branches = branch_filter(retrieval_filter).should
    team_branch = next(
        b for b in branches
        if isinstance(b, Filter)
        and any(c.key == "access_scope" and c.match.value == "team" for c in b.must)
    )

    team_id_condition = next(c for c in team_branch.must if c.key == "team_id")
    assert isinstance(team_id_condition.match, MatchAny)
    assert set(team_id_condition.match.any) == {1, 2, 3}


def test_team_branch_requires_organisation_id():
    repository = make_dense_repository_with_fake_client()
    access = make_access(organisation_id=42, team_ids=(1,))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branches = branch_filter(retrieval_filter).should
    team_branch = next(
        b for b in branches
        if isinstance(b, Filter)
        and any(c.key == "access_scope" and c.match.value == "team" for c in b.must)
    )

    org_condition = next(c for c in team_branch.must if c.key == "organisation_id")
    assert org_condition.match.value == 42


def test_different_team_ids_produce_different_filter_values():
    repository = make_dense_repository_with_fake_client()

    filter_a, _ = call_hybrid_search(repository, make_access(team_ids=(1, 2)))
    filter_b, _ = call_hybrid_search(repository, make_access(team_ids=(5, 6)))

    def team_ids_of(retrieval_filter):
        branches = branch_filter(retrieval_filter).should
        team_branch = next(
            b for b in branches
            if isinstance(b, Filter)
            and any(c.key == "access_scope" and c.match.value == "team" for c in b.must)
        )
        return set(next(c for c in team_branch.must if c.key == "team_id").match.any)

    assert team_ids_of(filter_a) != team_ids_of(filter_b)


def test_zero_team_user_has_no_team_branch():
    repository = make_dense_repository_with_fake_client()
    access = make_access(team_ids=())

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branches = branch_filter(retrieval_filter).should

    team_branches = [
        b for b in branches
        if isinstance(b, Filter)
        and any(c.key == "access_scope" and c.match.value == "team" for c in b.must)
    ]
    assert team_branches == []


def test_matchany_with_empty_list_is_never_generated():
    repository = make_dense_repository_with_fake_client()

    for access in (
        make_access(team_ids=()),
        make_access(team_ids=(1,)),
        make_access(team_ids=(1, 2, 3), role=OrgRole.ADMIN),
        make_access(team_ids=(), role=OrgRole.ADMIN),
    ):
        retrieval_filter, _ = call_hybrid_search(repository, access)
        for match_any in find_matchany(retrieval_filter):
            assert match_any.any != []


# --------------------------------------------------------------------------- #
# C. Organisation
# --------------------------------------------------------------------------- #


def _organisation_branches(retrieval_filter: Filter):
    branches = branch_filter(retrieval_filter).should
    return [
        b for b in branches
        if isinstance(b, Filter)
        and any(c.key == "access_scope" and c.match.value == "organisation" for c in b.must)
    ]


def _team_branches(retrieval_filter: Filter):
    branches = branch_filter(retrieval_filter).should
    return [
        b for b in branches
        if isinstance(b, Filter)
        and any(c.key == "access_scope" and c.match.value == "team" for c in b.must)
    ]


def _admin_team_branches(retrieval_filter: Filter):
    """RBAC-5J: the ADMIN blanket-TEAM branch is the one TEAM branch with
    no ``team_id`` condition at all -- distinct from both the membership
    branch (team_id from access.team_ids) and the jurisdiction branch
    (team_id from access.jurisdiction_team_ids), which both carry one."""

    return [
        b for b in _team_branches(retrieval_filter)
        if not any(c.key == "team_id" for c in b.must)
    ]


def _jurisdiction_team_branches(retrieval_filter: Filter, jurisdiction_team_ids):
    """The TEAM branch whose team_id MatchAny matches exactly the given
    jurisdiction team ids -- distinguishes it from a membership branch
    that might otherwise carry a different team_ids value."""

    target = set(jurisdiction_team_ids)
    matches = []
    for b in _team_branches(retrieval_filter):
        team_id_conditions = [c for c in b.must if c.key == "team_id"]
        if team_id_conditions and set(team_id_conditions[0].match.any) == target:
            matches.append(b)
    return matches


def test_admin_receives_organisation_branch():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    assert len(_organisation_branches(retrieval_filter)) == 1


def test_organisation_branch_contains_organisation_id():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, organisation_id=99)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    org_branch = _organisation_branches(retrieval_filter)[0]
    org_condition = next(c for c in org_branch.must if c.key == "organisation_id")
    assert org_condition.match.value == 99


def test_member_does_not_receive_organisation_branch():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MEMBER)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    assert _organisation_branches(retrieval_filter) == []


def test_manager_does_not_receive_organisation_branch():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MANAGER)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    assert _organisation_branches(retrieval_filter) == []


def test_cross_organisation_isolation_for_admin():
    repository = make_dense_repository_with_fake_client()

    filter_a, _ = call_hybrid_search(repository, make_access(role=OrgRole.ADMIN, organisation_id=1))
    filter_b, _ = call_hybrid_search(repository, make_access(role=OrgRole.ADMIN, organisation_id=2))

    org_id_a = next(
        c.match.value for c in _organisation_branches(filter_a)[0].must if c.key == "organisation_id"
    )
    org_id_b = next(
        c.match.value for c in _organisation_branches(filter_b)[0].must if c.key == "organisation_id"
    )
    assert org_id_a != org_id_b


def test_role_is_never_encoded_as_a_qdrant_filter_condition():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, team_ids=(1,))

    retrieval_filter, _ = call_hybrid_search(repository, access)

    def all_keys(node) -> set[str]:
        keys: set[str] = set()

        def walk(value):
            if isinstance(value, Filter):
                for group in (value.must, value.should, value.must_not):
                    if group is None:
                        continue
                    items = group if isinstance(group, list) else [group]
                    for item in items:
                        walk(item)
            elif hasattr(value, "key"):
                keys.add(value.key)

        walk(node)
        return keys

    assert "role" not in all_keys(retrieval_filter)


# --------------------------------------------------------------------------- #
# D. Combined scopes
# --------------------------------------------------------------------------- #


def _branch_count(retrieval_filter: Filter) -> int:
    return len(branch_filter(retrieval_filter).should)


def test_admin_with_teams_gets_individual_team_organisation_and_admin_team():
    """RBAC-5J: ADMIN additionally receives an unconditional TEAM branch
    (all TEAM documents in their own organisation) alongside the
    pre-existing membership-based TEAM branch -- both are separate OR
    branches, so an ADMIN who also happens to be a team member gets 4
    branches total, not 3."""

    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, team_ids=(1, 2))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    assert _branch_count(retrieval_filter) == 4


def test_member_or_manager_with_teams_gets_individual_and_team_only():
    repository = make_dense_repository_with_fake_client()

    for role in (OrgRole.MEMBER, OrgRole.MANAGER):
        retrieval_filter, _ = call_hybrid_search(
            repository, make_access(role=role, team_ids=(1,)),
        )
        assert _branch_count(retrieval_filter) == 2
        assert _organisation_branches(retrieval_filter) == []


def test_zero_teams_non_admin_gets_individual_only():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MEMBER, team_ids=())

    retrieval_filter, _ = call_hybrid_search(repository, access)
    assert _branch_count(retrieval_filter) == 1


def test_zero_teams_admin_gets_individual_organisation_and_admin_team():
    """RBAC-5J: even with zero team memberships, ADMIN still receives
    the unconditional TEAM branch -- ADMIN's TEAM visibility never
    depends on team_ids."""

    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, team_ids=())

    retrieval_filter, _ = call_hybrid_search(repository, access)
    assert _branch_count(retrieval_filter) == 3
    assert len(_organisation_branches(retrieval_filter)) == 1
    assert len(_admin_team_branches(retrieval_filter)) == 1


# --------------------------------------------------------------------------- #
# E. Structural filters
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "access",
    [
        make_access(),
        make_access(team_ids=(1, 2)),
        make_access(role=OrgRole.ADMIN),
        make_access(role=OrgRole.ADMIN, team_ids=(1,)),
    ],
)
def test_structural_filters_always_present(access):
    repository = make_dense_repository_with_fake_client()

    retrieval_filter, _ = call_hybrid_search(repository, access)

    top_level_conditions = [c for c in retrieval_filter.must if hasattr(c, "key")]
    conditions = {c.key: c.match.value for c in top_level_conditions}
    assert conditions["is_reference"] is False
    assert conditions["is_appendix"] is False


# --------------------------------------------------------------------------- #
# F. Legacy v2
# --------------------------------------------------------------------------- #


def test_individual_branch_contains_is_empty_condition_for_access_scope():
    repository = make_dense_repository_with_fake_client()
    access = make_access()

    retrieval_filter, _ = call_hybrid_search(repository, access)
    individual = branch_filter(retrieval_filter).should[0]

    is_empty_conditions = [c for c in individual.should if isinstance(c, IsEmptyCondition)]
    assert len(is_empty_conditions) == 1
    assert is_empty_conditions[0].is_empty.key == "access_scope"


def test_individual_branch_still_requires_user_id_alongside_is_empty():
    repository = make_dense_repository_with_fake_client()
    access = make_access(user_id=42)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    individual = branch_filter(retrieval_filter).should[0]

    # The IsEmptyCondition lives in `should` (an OR alternative to the
    # explicit access_scope=="individual" match); user_id ownership lives
    # in `must` and is never relaxed regardless of which should-branch fires.
    assert individual.must[0].key == "user_id"
    assert individual.must[0].match.value == 42


def test_team_and_organisation_branches_never_use_is_empty_condition():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, team_ids=(1,))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branches = branch_filter(retrieval_filter).should

    non_individual = branches[1:]
    for branch in non_individual:
        assert isinstance(branch, Filter)
        access_scope_conditions = [c for c in branch.must if c.key == "access_scope"]
        assert len(access_scope_conditions) == 1
        assert isinstance(access_scope_conditions[0].match, MatchValue)
        assert access_scope_conditions[0].match.value in ("team", "organisation")
        # No IsEmptyCondition anywhere in a TEAM/ORGANISATION branch --
        # a legacy point with a missing access_scope can never satisfy
        # these branches' explicit MatchValue requirement.
        assert not any(isinstance(c, IsEmptyCondition) for c in branch.must)


# --------------------------------------------------------------------------- #
# G. Dense/sparse consistency
# --------------------------------------------------------------------------- #


def test_dense_and_sparse_prefetch_share_the_same_filter_object():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, team_ids=(1, 2))

    dense_filter, sparse_filter = call_hybrid_search(repository, access)

    assert dense_filter == sparse_filter


# --------------------------------------------------------------------------- #
# H. RBAC-5J: Org Manager jurisdiction
# --------------------------------------------------------------------------- #


def test_jurisdiction_branch_exists_for_manager_with_jurisdiction():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MANAGER, jurisdiction_team_ids=(10, 11))

    retrieval_filter, _ = call_hybrid_search(repository, access)

    assert len(_jurisdiction_team_branches(retrieval_filter, (10, 11))) == 1


def test_jurisdiction_branch_absent_for_manager_without_jurisdiction():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MANAGER, jurisdiction_team_ids=())

    retrieval_filter, _ = call_hybrid_search(repository, access)

    assert _team_branches(retrieval_filter) == []


def test_jurisdiction_branch_absent_for_member_even_with_jurisdiction_ids():
    """jurisdiction_team_ids alone never grants a branch -- role must
    also be OrgRole.MANAGER. A plain MEMBER can never have jurisdiction
    in practice, but the filter must not trust the tuple's mere presence
    over the role."""

    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MEMBER, jurisdiction_team_ids=(10,))

    retrieval_filter, _ = call_hybrid_search(repository, access)

    assert _jurisdiction_team_branches(retrieval_filter, (10,)) == []


def test_jurisdiction_branch_absent_for_admin_even_with_jurisdiction_ids():
    """ADMIN's TEAM visibility comes from the unconditional admin-team
    branch, never the jurisdiction branch -- jurisdiction_team_ids on an
    ADMIN (however it got there) must not produce a second, narrower
    team_id-scoped branch alongside the blanket one."""

    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, jurisdiction_team_ids=(10,))

    retrieval_filter, _ = call_hybrid_search(repository, access)

    assert _jurisdiction_team_branches(retrieval_filter, (10,)) == []
    assert len(_admin_team_branches(retrieval_filter)) == 1


def test_jurisdiction_matchany_contains_supplied_jurisdiction_ids():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MANAGER, jurisdiction_team_ids=(3, 1, 2))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branch = _jurisdiction_team_branches(retrieval_filter, (1, 2, 3))[0]

    team_id_condition = next(c for c in branch.must if c.key == "team_id")
    assert set(team_id_condition.match.any) == {1, 2, 3}


def test_jurisdiction_branch_requires_organisation_id():
    repository = make_dense_repository_with_fake_client()
    access = make_access(
        role=OrgRole.MANAGER, organisation_id=42, jurisdiction_team_ids=(1,),
    )

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branch = _jurisdiction_team_branches(retrieval_filter, (1,))[0]

    org_condition = next(c for c in branch.must if c.key == "organisation_id")
    assert org_condition.match.value == 42


def test_jurisdiction_branch_does_not_require_user_id():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.MANAGER, jurisdiction_team_ids=(1,))

    retrieval_filter, _ = call_hybrid_search(repository, access)
    branch = _jurisdiction_team_branches(retrieval_filter, (1,))[0]

    assert "user_id" not in {c.key for c in branch.must}


def test_jurisdiction_matchany_with_empty_list_is_never_generated():
    repository = make_dense_repository_with_fake_client()

    for access in (
        make_access(role=OrgRole.MANAGER, jurisdiction_team_ids=()),
        make_access(role=OrgRole.MANAGER, jurisdiction_team_ids=(1,)),
        make_access(role=OrgRole.ADMIN, jurisdiction_team_ids=(1, 2, 3)),
    ):
        retrieval_filter, _ = call_hybrid_search(repository, access)
        for match_any in find_matchany(retrieval_filter):
            assert match_any.any != []


def test_admin_team_branch_has_no_team_id_condition():
    """The ADMIN blanket-TEAM branch is unconditional over every TEAM
    document in the organisation -- it must never carry a team_id
    condition (that would narrow it back down to a specific set)."""

    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    admin_branches = _admin_team_branches(retrieval_filter)

    assert len(admin_branches) == 1
    assert "team_id" not in {c.key for c in admin_branches[0].must}


def test_admin_team_branch_requires_organisation_id():
    repository = make_dense_repository_with_fake_client()
    access = make_access(role=OrgRole.ADMIN, organisation_id=77)

    retrieval_filter, _ = call_hybrid_search(repository, access)
    admin_branch = _admin_team_branches(retrieval_filter)[0]

    org_condition = next(c for c in admin_branch.must if c.key == "organisation_id")
    assert org_condition.match.value == 77


def test_manager_and_member_never_receive_admin_team_branch():
    repository = make_dense_repository_with_fake_client()

    for role in (OrgRole.MEMBER, OrgRole.MANAGER):
        retrieval_filter, _ = call_hybrid_search(repository, make_access(role=role))
        assert _admin_team_branches(retrieval_filter) == []
