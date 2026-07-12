"""baseline schema

Revision ID: 0001
Revises: 
Create Date: 2026-07-12 14:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enums
    campaign_status_enum = sa.Enum('IMPORTED', 'PROCESSING', 'PROCESSED', 'FAILED', 'ARCHIVED', name='campaignstatus')

    # Create Projects
    op.create_table('projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('video_count', sa.Integer(), nullable=False),
        sa.Column('thumbnail_path', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Video Assets
    op.create_table('video_assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('file_extension', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('fps', sa.Float(), nullable=True),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('resolution_w', sa.Integer(), nullable=False),
        sa.Column('resolution_h', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Clip Segments
    op.create_table('clip_segments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('video_asset_id', sa.String(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('hook_text', sa.String(), nullable=False),
        sa.Column('hashtags', sa.JSON(), nullable=False),
        sa.Column('captions', sa.JSON(), nullable=False),
        sa.Column('thumbnail_timestamp', sa.Float(), nullable=False),
        sa.Column('virality_score', sa.Integer(), nullable=False),
        sa.Column('ai_rationale', sa.String(), nullable=False),
        sa.Column('user_approved', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['video_asset_id'], ['video_assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Timeline Contexts
    op.create_table('timeline_contexts',
        sa.Column('video_asset_id', sa.String(), nullable=False),
        sa.Column('words_json', sa.JSON(), nullable=False),
        sa.Column('speakers_json', sa.JSON(), nullable=False),
        sa.Column('energy_json', sa.JSON(), nullable=False),
        sa.Column('silences_json', sa.JSON(), nullable=False),
        sa.Column('scenes_json', sa.JSON(), nullable=False),
        sa.Column('faces_json', sa.JSON(), nullable=False),
        sa.Column('emotions_json', sa.JSON(), nullable=False),
        sa.Column('gestures_json', sa.JSON(), nullable=False),
        sa.Column('objects_json', sa.JSON(), nullable=False),
        sa.Column('ocr_texts_json', sa.JSON(), nullable=False),
        sa.Column('topics_json', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['video_asset_id'], ['video_assets.id'], ),
        sa.PrimaryKeyConstraint('video_asset_id')
    )

    # Create Campaigns (BEFORE 28eba1110686 columns)
    op.create_table('campaigns',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=False),
        sa.Column('campaign_url', sa.String(), nullable=False),
        sa.Column('platforms', sa.JSON(), nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('payout', sa.String(), nullable=False),
        sa.Column('reward_type', sa.String(), nullable=False),
        sa.Column('rules_json', sa.JSON(), nullable=True),
        sa.Column('summary_json', sa.JSON(), nullable=True),
        sa.Column('worth_it_score_json', sa.JSON(), nullable=True),
        sa.Column('raw_content', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('status', campaign_status_enum, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Campaign Import History
    op.create_table('campaign_import_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=True),
        sa.Column('import_timestamp', sa.DateTime(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('processing_status', sa.String(), nullable=False),
        sa.Column('processing_duration_ms', sa.Integer(), nullable=False),
        sa.Column('duplicate_status', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('campaign_import_history')
    op.drop_table('campaigns')
    op.drop_table('timeline_contexts')
    op.drop_table('clip_segments')
    op.drop_table('video_assets')
    op.drop_table('projects')
