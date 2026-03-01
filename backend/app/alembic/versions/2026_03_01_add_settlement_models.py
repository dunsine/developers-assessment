"""Add settlement models

Revision ID: a1b2c3d4e5f6
Revises: 1a31ce608336
Create Date: 2026-03-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'worklog',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('task_name', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_worklog_user_id'), 'worklog', ['user_id'], unique=False)
    op.create_index(op.f('ix_worklog_created_at'), 'worklog', ['created_at'], unique=False)

    op.create_table(
        'time_segment',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('worklog_id', sa.UUID(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('hourly_rate', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['worklog_id'], ['worklog.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_time_segment_worklog_id'), 'time_segment', ['worklog_id'], unique=False)

    op.create_table(
        'adjustment',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('worklog_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('reason', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['worklog_id'], ['worklog.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_adjustment_worklog_id'), 'adjustment', ['worklog_id'], unique=False)

    op.create_table(
        'remittance',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_remittance_user_id'), 'remittance', ['user_id'], unique=False)
    op.create_index(op.f('ix_remittance_period_start'), 'remittance', ['period_start'], unique=False)
    op.create_index(op.f('ix_remittance_period_end'), 'remittance', ['period_end'], unique=False)
    op.create_index(op.f('ix_remittance_status'), 'remittance', ['status'], unique=False)

    op.create_table(
        'remittance_worklog',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('remittance_id', sa.UUID(), nullable=False),
        sa.Column('worklog_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['remittance_id'], ['remittance.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['worklog_id'], ['worklog.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_remittance_worklog_remittance_id'), 'remittance_worklog', ['remittance_id'], unique=False)
    op.create_index(op.f('ix_remittance_worklog_worklog_id'), 'remittance_worklog', ['worklog_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_remittance_worklog_worklog_id'), table_name='remittance_worklog')
    op.drop_index(op.f('ix_remittance_worklog_remittance_id'), table_name='remittance_worklog')
    op.drop_table('remittance_worklog')

    op.drop_index(op.f('ix_remittance_status'), table_name='remittance')
    op.drop_index(op.f('ix_remittance_period_end'), table_name='remittance')
    op.drop_index(op.f('ix_remittance_period_start'), table_name='remittance')
    op.drop_index(op.f('ix_remittance_user_id'), table_name='remittance')
    op.drop_table('remittance')

    op.drop_index(op.f('ix_adjustment_worklog_id'), table_name='adjustment')
    op.drop_table('adjustment')

    op.drop_index(op.f('ix_time_segment_worklog_id'), table_name='time_segment')
    op.drop_table('time_segment')

    op.drop_index(op.f('ix_worklog_created_at'), table_name='worklog')
    op.drop_index(op.f('ix_worklog_user_id'), table_name='worklog')
    op.drop_table('worklog')
