"""planning history

Revision ID: 9f476b0eafb1
Revises: b4c8f7549ae2
Create Date: 2026-07-12 20:25:20.479148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f476b0eafb1'
down_revision: Union[str, Sequence[str], None] = 'b4c8f7549ae2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('planning_pipeline_results')
    op.create_table('planning_pipeline_results',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('campaign_id', sa.String(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('planner_model', sa.String(), nullable=False),
    sa.Column('planning_version', sa.String(), nullable=False),
    sa.Column('pipeline_status', sa.Enum('NOT_STARTED', 'RUNNING', 'EXECUTION_PLAN_COMPLETE', 'CLIP_STRATEGY_COMPLETE', 'PROMPT_TEMPLATE_COMPLETE', 'SUITABILITY_COMPLETE', 'COMPLETED', 'FAILED', name='pipelinestatus'), nullable=False),
    sa.Column('validation_status', sa.Enum('PENDING', 'VALID', 'INVALID', name='validationstatus'), nullable=False),
    sa.Column('overall_confidence', sa.Float(), nullable=False),
    sa.Column('execution_duration_ms', sa.Integer(), nullable=False),
    sa.Column('generated_at', sa.DateTime(), nullable=False),
    sa.Column('execution_plan_json', sa.JSON(), nullable=True),
    sa.Column('clip_strategy_json', sa.JSON(), nullable=True),
    sa.Column('prompt_template_json', sa.JSON(), nullable=True),
    sa.Column('suitability_assessment_json', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('planning_pipeline_results')
    op.create_table('planning_pipeline_results',
    sa.Column('campaign_id', sa.VARCHAR(), nullable=False),
    sa.Column('planner_model', sa.VARCHAR(), nullable=False),
    sa.Column('planning_version', sa.VARCHAR(), nullable=False),
    sa.Column('pipeline_status', sa.VARCHAR(length=24), nullable=False),
    sa.Column('validation_status', sa.VARCHAR(length=7), nullable=False),
    sa.Column('overall_confidence', sa.FLOAT(), nullable=False),
    sa.Column('execution_duration_ms', sa.INTEGER(), nullable=False),
    sa.Column('generated_at', sa.DATETIME(), nullable=False),
    sa.Column('execution_plan_json', sa.JSON(), nullable=True),
    sa.Column('clip_strategy_json', sa.JSON(), nullable=True),
    sa.Column('prompt_template_json', sa.JSON(), nullable=True),
    sa.Column('suitability_assessment_json', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('campaign_id')
    )
