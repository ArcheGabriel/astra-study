"""rbac org manager team jurisdiction

Revision ID: d18a69b8ede3
Revises: 116ced32c143
Create Date: 2026-09-27 13:11:14.744040

Introduces ``org_manager_teams``: the many-to-many jurisdiction
relationship between an ``OrgRole.MANAGER`` and the teams they
supervise (RBAC-5J). Purely additive -- no existing table is altered,
no data is backfilled, and no row is auto-created; a jurisdiction row
only ever exists after an explicit ``OrgRole.ADMIN`` grant.

Structurally independent of ``team_memberships`` (RBAC foundation
migration, 116ced32c143): jurisdiction never implies, and is never
implied by, team membership.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd18a69b8ede3'
down_revision: Union[str, Sequence[str], None] = '116ced32c143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'org_manager_teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'team_id', name='uq_org_manager_teams_user_id_team_id'),
    )
    op.create_index(op.f('ix_org_manager_teams_user_id'), 'org_manager_teams', ['user_id'], unique=False)
    op.create_index(op.f('ix_org_manager_teams_team_id'), 'org_manager_teams', ['team_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f('ix_org_manager_teams_team_id'), table_name='org_manager_teams')
    op.drop_index(op.f('ix_org_manager_teams_user_id'), table_name='org_manager_teams')
    op.drop_table('org_manager_teams')
