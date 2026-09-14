"""rbac organisation/team foundation

Revision ID: 116ced32c143
Revises: 643a02aac7aa
Create Date: 2026-09-14 00:00:00.000000

Establishes the relational foundation for RBAC:

- ``organisations``, ``teams``, ``team_memberships`` tables.
- ``users.organisation_id`` / ``users.role`` (every existing user is
  attached to a single seeded "Default Organisation" and set to MEMBER).
- ``documents.organisation_id`` / ``documents.team_id`` / ``documents.access_scope``
  (every existing document is backfilled to its uploader's organisation,
  ``access_scope='individual'``, ``team_id=NULL`` -- unchanged from today's
  behaviour).

This migration is purely relational. It does NOT create an ADMIN user
(bootstrap is a separate, explicit, later step -- see
``scripts/grant_admin.py``), and it does not touch Qdrant, stored files,
or document ingestion in any way.

Written to work on both SQLite (dev/tests) and PostgreSQL (production):
NOT NULL columns that require a computed backfill are added nullable,
backfilled via a data UPDATE, then tightened via ``batch_alter_table``
(direct ALTER on Postgres, table-recreate on SQLite) -- mirroring how
this project already renders ``Enum`` columns (see ``documentstatus`` /
``messagerole`` in earlier migrations).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '116ced32c143'
down_revision: Union[str, Sequence[str], None] = '643a02aac7aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_ORGANISATION_NAME = "Default Organisation"
DEFAULT_ORGANISATION_SLUG = "default"


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Organisation structure
    # ------------------------------------------------------------------
    op.create_table(
        'organisations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    # ------------------------------------------------------------------
    # 2. Seed the default organisation
    # ------------------------------------------------------------------
    bind.execute(
        sa.text(
            "INSERT INTO organisations (name, slug, created_at, updated_at) "
            "VALUES (:name, :slug, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ),
        {"name": DEFAULT_ORGANISATION_NAME, "slug": DEFAULT_ORGANISATION_SLUG},
    )
    default_organisation_id = bind.execute(
        sa.text("SELECT id FROM organisations WHERE slug = :slug"),
        {"slug": DEFAULT_ORGANISATION_SLUG},
    ).scalar_one()

    # ------------------------------------------------------------------
    # 3. users.organisation_id / users.role -- add nullable first
    # ------------------------------------------------------------------
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('organisation_id', sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column(
                'role',
                sa.Enum('member', 'manager', 'admin', name='orgrole'),
                nullable=True,
            )
        )

    # ------------------------------------------------------------------
    # 4. Assign ALL existing users to the default organisation, as MEMBER
    #    -- migration MUST NOT create an ADMIN.
    # ------------------------------------------------------------------
    bind.execute(
        sa.text("UPDATE users SET organisation_id = :org_id, role = 'member'"),
        {"org_id": default_organisation_id},
    )

    # ------------------------------------------------------------------
    # 5. users -- enforce NOT NULL + FK + index now that every row is populated
    # ------------------------------------------------------------------
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('organisation_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column(
            'role',
            existing_type=sa.Enum('member', 'manager', 'admin', name='orgrole'),
            nullable=False,
        )
        batch_op.create_index(op.f('ix_users_organisation_id'), ['organisation_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_users_organisation_id_organisations',
            'organisations',
            ['organisation_id'],
            ['id'],
        )

    # ------------------------------------------------------------------
    # 6. Team
    # ------------------------------------------------------------------
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organisation_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['organisation_id'], ['organisations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organisation_id', 'name', name='uq_teams_organisation_id_name'),
    )
    op.create_index(op.f('ix_teams_organisation_id'), 'teams', ['organisation_id'], unique=False)

    # ------------------------------------------------------------------
    # 7. TeamMembership
    # ------------------------------------------------------------------
    op.create_table(
        'team_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('member', 'manager', name='teamrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'team_id', name='uq_team_memberships_user_id_team_id'),
    )
    op.create_index(op.f('ix_team_memberships_user_id'), 'team_memberships', ['user_id'], unique=False)
    op.create_index(op.f('ix_team_memberships_team_id'), 'team_memberships', ['team_id'], unique=False)

    # ------------------------------------------------------------------
    # 8. documents.organisation_id / team_id / access_scope -- add nullable first
    # ------------------------------------------------------------------
    with op.batch_alter_table('documents') as batch_op:
        batch_op.add_column(sa.Column('organisation_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('team_id', sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column(
                'access_scope',
                sa.Enum('individual', 'team', 'organisation', name='documentaccessscope'),
                nullable=True,
            )
        )

    # ------------------------------------------------------------------
    # 9. Populate existing documents:
    #      organisation_id = uploader's organisation_id
    #      access_scope    = individual
    #      team_id         = NULL (unchanged, already NULL)
    # ------------------------------------------------------------------
    bind.execute(
        sa.text(
            "UPDATE documents SET "
            "organisation_id = (SELECT organisation_id FROM users WHERE users.id = documents.user_id), "
            "access_scope = 'individual'"
        )
    )

    # ------------------------------------------------------------------
    # 10. documents -- enforce NOT NULL (organisation_id, access_scope) + FKs + indexes.
    #     team_id remains nullable by design.
    # ------------------------------------------------------------------
    with op.batch_alter_table('documents') as batch_op:
        batch_op.alter_column('organisation_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column(
            'access_scope',
            existing_type=sa.Enum('individual', 'team', 'organisation', name='documentaccessscope'),
            nullable=False,
        )
        batch_op.create_index(op.f('ix_documents_organisation_id'), ['organisation_id'], unique=False)
        batch_op.create_index(op.f('ix_documents_team_id'), ['team_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_documents_organisation_id_organisations',
            'organisations',
            ['organisation_id'],
            ['id'],
        )
        batch_op.create_foreign_key(
            'fk_documents_team_id_teams',
            'teams',
            ['team_id'],
            ['id'],
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table('documents') as batch_op:
        batch_op.drop_constraint('fk_documents_team_id_teams', type_='foreignkey')
        batch_op.drop_constraint('fk_documents_organisation_id_organisations', type_='foreignkey')
        batch_op.drop_index(op.f('ix_documents_team_id'))
        batch_op.drop_index(op.f('ix_documents_organisation_id'))
        batch_op.drop_column('access_scope')
        batch_op.drop_column('team_id')
        batch_op.drop_column('organisation_id')

    op.drop_index(op.f('ix_team_memberships_team_id'), table_name='team_memberships')
    op.drop_index(op.f('ix_team_memberships_user_id'), table_name='team_memberships')
    op.drop_table('team_memberships')

    op.drop_index(op.f('ix_teams_organisation_id'), table_name='teams')
    op.drop_table('teams')

    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('fk_users_organisation_id_organisations', type_='foreignkey')
        batch_op.drop_index(op.f('ix_users_organisation_id'))
        batch_op.drop_column('role')
        batch_op.drop_column('organisation_id')

    op.drop_table('organisations')

    # team_memberships' 'teamrole' type is auto-dropped with its owning table
    # above (create_table/drop_table lifecycle). 'orgrole' and
    # 'documentaccessscope' were added to EXISTING tables via add_column, so
    # no table-drop event fires to clean them up -- drop them explicitly.
    # A no-op on SQLite (no native enum type); drops the PostgreSQL TYPE.
    sa.Enum(name='documentaccessscope').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='orgrole').drop(op.get_bind(), checkfirst=True)
