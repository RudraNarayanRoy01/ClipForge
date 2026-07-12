"""add_campaign_planning_columns

Revision ID: 28eba1110686
Revises: 
Create Date: 2026-07-12 01:36:47.112830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28eba1110686'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('campaigns', sa.Column('execution_plan_json', sa.JSON(), nullable=True))
    op.add_column('campaigns', sa.Column('clip_strategy_json', sa.JSON(), nullable=True))
    op.add_column('campaigns', sa.Column('prompt_template_json', sa.JSON(), nullable=True))
    op.add_column('campaigns', sa.Column('suitability_assessment_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('campaigns', 'suitability_assessment_json')
    op.drop_column('campaigns', 'prompt_template_json')
    op.drop_column('campaigns', 'clip_strategy_json')
    op.drop_column('campaigns', 'execution_plan_json')
