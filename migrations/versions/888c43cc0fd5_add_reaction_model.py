"""Add Reaction model

Revision ID: 888c43cc0fd5
Revises: f638c7c240bc
Create Date: 2025-06-25 19:56:58.898124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '888c43cc0fd5'
down_revision = 'f638c7c240bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'post_id', name='unique_user_post_reaction')
    )
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('cheers')
        batch_op.drop_column('boos')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('boos', sa.INTEGER(), server_default=sa.text("'0'"), nullable=False))
        batch_op.add_column(sa.Column('cheers', sa.INTEGER(), server_default=sa.text("'0'"), nullable=False))

    op.drop_table('reaction')
    # ### end Alembic commands ###
