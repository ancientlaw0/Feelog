"""Added profile_image to User model

Revision ID: 81de5b2f5de1
Revises: 7b309eba5bbd
Create Date: 2025-06-20 16:53:31.417741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81de5b2f5de1'
down_revision = '7b309eba5bbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_image', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('profile_image')

    # ### end Alembic commands ###
