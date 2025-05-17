"""описание_изменений

Revision ID: 6f9bf7c65ee0
Revises: 
Create Date: 2025-05-17 02:34:22.029285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f9bf7c65ee0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'buildings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('address', sa.String(), nullable=False, index=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
    )
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('activities.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), index=True),
        sa.Column('building_id', sa.Integer(), sa.ForeignKey('buildings.id'), nullable=True),
    )
    op.create_table(
        'phone_numbers',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('number', sa.String(), nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_table(
        'organization_activity',
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('activity_id', sa.Integer(), sa.ForeignKey('activities.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('organization_activity')
    op.drop_table('phone_numbers')
    op.drop_table('organizations')
    op.drop_table('activities')
    op.drop_table('buildings')
