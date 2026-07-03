from collections.abc import Sequence
from datetime import datetime, timezone
import sqlalchemy as sa
from alembic import op


revision: str = '67c6b491714b'
down_revision: str | None = None
branch_labels: Sequence[str] | str | None = None
depends_on: Sequence[str] | str | None = None


def upgrade() -> None:
    op.create_table('hotspots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('risk_score', sa.Float(), nullable=False),
    sa.Column('cluster_size', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'MONITORING', 'RESOLVED', name='hotspot_status'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hotspots_created_at'), 'hotspots', ['created_at'], unique=False)
    op.create_index(op.f('ix_hotspots_id'), 'hotspots', ['id'], unique=False)
    op.create_table('predictions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('predicted_aqi', sa.Float(), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('risk_level', sa.Enum('LOW', 'MODERATE', 'HIGH', 'SEVERE', name='risk_level'), nullable=False),
    sa.Column('prediction_time', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_created_at'), 'predictions', ['created_at'], unique=False)
    op.create_index(op.f('ix_predictions_id'), 'predictions', ['id'], unique=False)
    op.create_table('sensor_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('aqi', sa.Float(), nullable=False),
    sa.Column('pm25', sa.Float(), nullable=False),
    sa.Column('pm10', sa.Float(), nullable=False),
    sa.Column('co', sa.Float(), nullable=False),
    sa.Column('no2', sa.Float(), nullable=False),
    sa.Column('temperature', sa.Float(), nullable=False),
    sa.Column('humidity', sa.Float(), nullable=False),
    sa.Column('wind_speed', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensor_data_id'), 'sensor_data', ['id'], unique=False)
    op.create_index(op.f('ix_sensor_data_timestamp'), 'sensor_data', ['timestamp'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('CITIZEN', 'MUNICIPALITY_ADMIN', name='user_role'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('alerts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hotspot_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('recommended_action', sa.String(length=500), nullable=False),
    sa.Column('status', sa.Enum('SENT', 'PENDING', 'RESOLVED', name='alert_status'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['hotspot_id'], ['hotspots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_created_at'), 'alerts', ['created_at'], unique=False)
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_table('pollution_reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('image_path', sa.String(length=500), nullable=False),
    sa.Column('processed_image_path', sa.String(length=500), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('address', sa.String(length=500), nullable=True),
    sa.Column('pollution_type', sa.Enum('SMOKE', 'DUST', 'GARBAGE_BURNING', 'CONSTRUCTION_DUST', 'INDUSTRIAL_SMOKE', 'OTHER', name='pollution_type'), nullable=False),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='severity_level'), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'VERIFIED', 'RESOLVED', name='report_status'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pollution_reports_created_at'), 'pollution_reports', ['created_at'], unique=False)
    op.create_index(op.f('ix_pollution_reports_id'), 'pollution_reports', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_pollution_reports_id'), table_name='pollution_reports')
    op.drop_index(op.f('ix_pollution_reports_created_at'), table_name='pollution_reports')
    op.drop_table('pollution_reports')
    op.drop_index(op.f('ix_alerts_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_created_at'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_sensor_data_timestamp'), table_name='sensor_data')
    op.drop_index(op.f('ix_sensor_data_id'), table_name='sensor_data')
    op.drop_table('sensor_data')
    op.drop_index(op.f('ix_predictions_id'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_created_at'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_index(op.f('ix_hotspots_id'), table_name='hotspots')
    op.drop_index(op.f('ix_hotspots_created_at'), table_name='hotspots')
    op.drop_table('hotspots')
