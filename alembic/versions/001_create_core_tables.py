"""create core tables

Revision ID: 001_create_core_tables
Revises:
Create Date: 2025-07-18

"""
from alembic import op
import sqlalchemy as sa

revision = '001_create_core_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('query', sa.String(255)),
        sa.Column('url', sa.String(255)),
        sa.Column('sessions', sa.Integer),
        sa.Column('config', sa.JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now())
    )
    op.create_table(
        'fingerprints',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('label', sa.String(128), nullable=True),  # например, имя профиля или сгенерированного шаблона
        sa.Column('data', sa.JSON, nullable=False),         # все поля fingerprint
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now())
    )
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('campaign_id', sa.Integer, sa.ForeignKey('campaigns.id')),
        sa.Column('status', sa.String(32), default='new'),
        sa.Column('started_at', sa.TIMESTAMP, nullable=True),
        sa.Column('finished_at', sa.TIMESTAMP, nullable=True),
        sa.Column('worker_id', sa.String(128), nullable=True),
        sa.Column('proxy_id', sa.Integer, nullable=True),
        sa.Column('profile_id', sa.Integer, nullable=True),
        sa.Column('fingerprint_id', sa.Integer, sa.ForeignKey('fingerprints.id'), nullable=True),
        sa.Column('fingerprint', sa.JSON, nullable=False, server_default='{}'),  # храним snapshot или runtime-отпечаток
        sa.Column('log', sa.JSON, nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now())
    )
    op.create_table(
        'job_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('job_id', sa.Integer, sa.ForeignKey('jobs.id')),
        sa.Column('event', sa.String(255)),
        sa.Column('message', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now())
    )
    op.create_table(
        'proxies',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('ip', sa.String(64)),
        sa.Column('port', sa.Integer),
        sa.Column('login', sa.String(128)),
        sa.Column('password', sa.String(128)),
        sa.Column('type', sa.String(16)),
        sa.Column('country', sa.String(64)),
        sa.Column('status', sa.String(32), default='active'),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now())
    )
    op.create_table(
        'antidetect_profiles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('external_id', sa.String(128)),
        sa.Column('provider', sa.String(32)),
        sa.Column('status', sa.String(32), default='active'),
        sa.Column('last_used_at', sa.TIMESTAMP, nullable=True)
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('telegram_id', sa.BigInteger, nullable=True),
        sa.Column('username', sa.String(64), nullable=True),
        sa.Column('role', sa.String(32), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now())
    )
    op.create_table(
        'worker_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('worker_id', sa.String(128)),
        sa.Column('url', sa.Text),
        sa.Column('action_type', sa.String(64)),
        sa.Column('action_data', sa.JSON, nullable=True),
        sa.Column('status', sa.String(32)),  # success, fail, skipped, etc.
        sa.Column('screenshot', sa.Text, nullable=True),  # путь или base64
        sa.Column('error_msg', sa.Text, nullable=True),
        sa.Column('started_at', sa.TIMESTAMP, nullable=True),
        sa.Column('finished_at', sa.TIMESTAMP, nullable=True),
        sa.Column('duration_ms', sa.Integer, nullable=True)
    )

def downgrade():
    op.drop_table('worker_logs')
    op.drop_table('users')
    op.drop_table('antidetect_profiles')
    op.drop_table('proxies')
    op.drop_table('job_logs')
    op.drop_table('jobs')
    op.drop_table('fingerprints')
    op.drop_table('campaigns')
