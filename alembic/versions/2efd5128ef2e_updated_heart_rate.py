"""Updated heart_rate

Revision ID: 2efd5128ef2e
Revises: b2fe954bd31d
Create Date: 2025-02-20 21:21:56.523792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2efd5128ef2e"
down_revision: Union[str, None] = "b2fe954bd31d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("run")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "run",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("date", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column(
            "distance",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "unit",
            postgresql.ENUM("MILES", "KILOMETERS", name="distanceunit"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "duration",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("heart_rate", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "elevation_gain",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "pace",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "run_type",
            postgresql.ENUM(
                "EASY", "LONG", "INTERVAL", "TEMPO", "RACE", "RECOVERY", name="runtype"
            ),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("location", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("notes", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="run_pkey"),
    )
    # ### end Alembic commands ###
