"""empty message

Revision ID: 61e997004b48
Revises: e3b13b49a5ac
Create Date: 2022-10-26 21:06:55.995396

"""
import sqlalchemy as sa  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision = "61e997004b48"
down_revision = "e3b13b49a5ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f("ix_text_result_is_processed"), "text_result", ["is_processed"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_text_result_is_processed"), table_name="text_result")
    # ### end Alembic commands ###