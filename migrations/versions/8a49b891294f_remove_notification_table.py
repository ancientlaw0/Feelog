"""Remove notification table

Revision ID: 8a49b891294f
Revises: df90e4cb4795
Create Date: 2025-07-02 23:19:48.042137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a49b891294f'
down_revision = 'df90e4cb4795'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notification_name'))
        batch_op.drop_index(batch_op.f('ix_notification_timestamp'))
        batch_op.drop_index(batch_op.f('ix_notification_user_id'))

    op.drop_table('notification')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('timestamp', sa.FLOAT(), nullable=False),
    sa.Column('payload_json', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notification_user_id'), ['user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_notification_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_notification_name'), ['name'], unique=False)

    # ### end Alembic commands ###
