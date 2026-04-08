"""Initial schema - all Phase 1 tables

Revision ID: 001_initial
Revises:
Create Date: 2026-04-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enums ---
    agegroup_enum = postgresql.ENUM(
        'children_5_12', 'teenagers_13_17', 'college_18_24', 'adults_25_59', 'elderly_60_plus',
        name='agegroup', create_type=True
    )
    userrole_enum = postgresql.ENUM('user', 'patient', 'therapist', 'admin', name='userrole', create_type=True)
    persona_enum = postgresql.ENUM(
        'manomitra', 'manospark', 'manoveil_core', 'manobalance', 'manosaathi', 'manoconnect',
        name='persona', create_type=True
    )
    assessmenttype_enum = postgresql.ENUM(
        'dass_21', 'gad_7', 'phq_9', 'cdi_2', 'scared', 'gds_15',
        name='assessmenttype', create_type=True
    )
    moodlevel_enum = postgresql.ENUM(
        'very_bad', 'bad', 'neutral', 'good', 'very_good',
        name='moodlevel', create_type=True
    )
    scorecategory_enum = postgresql.ENUM(
        'minimal', 'mild', 'moderate', 'moderately_severe', 'severe',
        name='scorecategory', create_type=True
    )
    crisisseverity_enum = postgresql.ENUM(
        'yellow_flag', 'orange', 'red', 'sos',
        name='crisisseverity', create_type=True
    )

    agegroup_enum.create(op.get_bind(), checkfirst=True)
    userrole_enum.create(op.get_bind(), checkfirst=True)
    persona_enum.create(op.get_bind(), checkfirst=True)
    assessmenttype_enum.create(op.get_bind(), checkfirst=True)
    moodlevel_enum.create(op.get_bind(), checkfirst=True)
    scorecategory_enum.create(op.get_bind(), checkfirst=True)
    crisisseverity_enum.create(op.get_bind(), checkfirst=True)

    # --- Users ---
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('age_group', agegroup_enum, nullable=False),
        sa.Column('role', userrole_enum, nullable=False),
        sa.Column('persona', persona_enum, nullable=False),
        sa.Column('emergency_contact_name', sa.String(255), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # --- Assessments ---
    op.create_table('assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_type', assessmenttype_enum, nullable=False),
        sa.Column('raw_responses', postgresql.JSONB(), nullable=False),
        sa.Column('total_score', sa.Float(), nullable=False),
        sa.Column('subscale_scores', postgresql.JSONB(), nullable=True),
        sa.Column('normalized_score', sa.Float(), nullable=False),
        sa.Column('category', scorecategory_enum, nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])

    # --- Mood Entries ---
    op.create_table('mood_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mood_level', moodlevel_enum, nullable=False),
        sa.Column('emoji', sa.String(10), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_mood_entries_user_id', 'mood_entries', ['user_id'])

    # --- Sleep Entries ---
    op.create_table('sleep_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sleep_duration', sa.Float(), nullable=False),
        sa.Column('sleep_quality', sa.Integer(), nullable=False),
        sa.Column('bedtime', sa.Time(), nullable=True),
        sa.Column('wake_time', sa.Time(), nullable=True),
        sa.Column('disturbances', sa.Integer(), default=0),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('sleep_quality BETWEEN 1 AND 5', name='sleep_quality_range'),
    )
    op.create_index('ix_sleep_entries_user_id', 'sleep_entries', ['user_id'])

    # --- Activity Entries ---
    op.create_table('activity_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activity_type', sa.String(100), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('intensity', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('intensity IS NULL OR intensity BETWEEN 1 AND 5', name='intensity_range'),
    )
    op.create_index('ix_activity_entries_user_id', 'activity_entries', ['user_id'])

    # --- Social Entries ---
    op.create_table('social_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interactions_count', sa.Integer(), nullable=False),
        sa.Column('quality_rating', sa.Integer(), nullable=False),
        sa.Column('isolation_feeling', sa.Integer(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('quality_rating BETWEEN 1 AND 5', name='quality_range'),
        sa.CheckConstraint('isolation_feeling BETWEEN 1 AND 5', name='isolation_range'),
    )
    op.create_index('ix_social_entries_user_id', 'social_entries', ['user_id'])

    # --- Chat Sessions ---
    op.create_table('chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('persona', persona_enum, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])

    # --- Chat Messages ---
    op.create_table('chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('crisis_flag', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])

    # --- Stress Scores ---
    op.create_table('stress_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('psychometric_score', sa.Float(), nullable=False),
        sa.Column('nlp_score', sa.Float(), nullable=False),
        sa.Column('fused_score', sa.Float(), nullable=False),
        sa.Column('category', scorecategory_enum, nullable=False),
        sa.Column('yellow_flag', sa.Boolean(), default=False),
        sa.Column('source_assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id'), nullable=True),
        sa.Column('source_chat_session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id'), nullable=True),
        sa.Column('shap_values', postgresql.JSONB(), nullable=True),
        sa.Column('feature_values', postgresql.JSONB(), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_stress_scores_user_id', 'stress_scores', ['user_id'])

    # --- Crisis Events ---
    op.create_table('crisis_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('severity', crisisseverity_enum, nullable=False),
        sa.Column('trigger_source', sa.String(50), nullable=False),
        sa.Column('trigger_score', sa.Float(), nullable=True),
        sa.Column('trigger_text', sa.Text(), nullable=True),
        sa.Column('action_taken', sa.String(100), nullable=False),
        sa.Column('resolved', sa.Boolean(), default=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_crisis_events_user_id', 'crisis_events', ['user_id'])

    # --- Patient-Therapist Links ---
    op.create_table('patient_therapist_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('therapist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('linked_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('unlinked_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('patient_id', 'therapist_id', name='uq_patient_therapist'),
    )
    op.create_index('ix_patient_therapist_links_patient_id', 'patient_therapist_links', ['patient_id'])
    op.create_index('ix_patient_therapist_links_therapist_id', 'patient_therapist_links', ['therapist_id'])

    # --- Therapist Notes ---
    op.create_table('therapist_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('therapist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('note_type', sa.String(50), default='session_note'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_therapist_notes_therapist_id', 'therapist_notes', ['therapist_id'])
    op.create_index('ix_therapist_notes_patient_id', 'therapist_notes', ['patient_id'])

    # --- Interventions ---
    op.create_table('interventions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('intervention_type', sa.String(50), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('target_personas', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('target_categories', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Intervention Completions ---
    op.create_table('intervention_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('intervention_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('interventions.id'), nullable=False),
        sa.Column('feedback_rating', sa.Integer(), nullable=True),
        sa.Column('feedback_note', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_intervention_completions_user_id', 'intervention_completions', ['user_id'])

    # --- Federated Rounds (BAFL Phase 2 placeholder) ---
    op.create_table('federated_rounds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('round_number', sa.Integer(), nullable=False, unique=True),
        sa.Column('participating_nodes', sa.Integer(), nullable=False),
        sa.Column('global_model_version', sa.String(100), nullable=False),
        sa.Column('aggregation_method', sa.String(50), default='fedavg'),
        sa.Column('global_accuracy', sa.Float(), nullable=True),
        sa.Column('global_loss', sa.Float(), nullable=True),
        sa.Column('ipfs_model_hash', sa.String(255), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Gradient Commits (BAFL Phase 2 placeholder) ---
    op.create_table('gradient_commits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('round_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution_pseudo_id', sa.String(255), nullable=False),
        sa.Column('gradient_hash', sa.String(255), nullable=False),
        sa.Column('encrypted_gradient_size', sa.Integer(), nullable=False),
        sa.Column('dp_epsilon_used', sa.Float(), nullable=False),
        sa.Column('dp_delta_used', sa.Float(), default=1e-5),
        sa.Column('zk_proof_valid', sa.Boolean(), default=False),
        sa.Column('zk_proof_hash', sa.String(255), nullable=True),
        sa.Column('fabric_tx_id', sa.String(255), nullable=True),
        sa.Column('fabric_block_number', sa.Integer(), nullable=True),
        sa.Column('ipfs_gradient_hash', sa.String(255), nullable=True),
        sa.Column('local_accuracy', sa.Float(), nullable=True),
        sa.Column('local_loss', sa.Float(), nullable=True),
        sa.Column('local_samples_count', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_gradient_commits_round_id', 'gradient_commits', ['round_id'])


def downgrade() -> None:
    op.drop_table('gradient_commits')
    op.drop_table('federated_rounds')
    op.drop_table('intervention_completions')
    op.drop_table('interventions')
    op.drop_table('therapist_notes')
    op.drop_table('patient_therapist_links')
    op.drop_table('crisis_events')
    op.drop_table('stress_scores')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('social_entries')
    op.drop_table('activity_entries')
    op.drop_table('sleep_entries')
    op.drop_table('mood_entries')
    op.drop_table('assessments')
    op.drop_table('users')

    # Drop enums
    for enum_name in ['crisisseverity', 'scorecategory', 'moodlevel', 'assessmenttype', 'persona', 'userrole', 'agegroup']:
        postgresql.ENUM(name=enum_name).drop(op.get_bind(), checkfirst=True)
