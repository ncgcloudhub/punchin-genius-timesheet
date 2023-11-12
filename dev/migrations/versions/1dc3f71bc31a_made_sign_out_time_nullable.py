"""Made sign_out_time nullable

Revision ID: 1dc3f71bc31a
Revises: fabdbf877fcc
Create Date: 2023-09-15 02:45:42.708585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1dc3f71bc31a'
down_revision = 'fabdbf877fcc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('time_entry', schema=None) as batch_op:
        batch_op.alter_column('sign_out_time',
               existing_type=sa.TIME(),
               type_=sa.DateTime(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('time_entry', schema=None) as batch_op:
        batch_op.alter_column('sign_out_time',
               existing_type=sa.DateTime(),
               type_=sa.TIME(),
               existing_nullable=True)

    # ### end Alembic commands ###
