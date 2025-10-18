"""create modules and tasks (retry)

Revision ID: f773d24842da
Revises: 5048e99f2987
Create Date: 2025-10-18 03:59:33.978086
"""

from alembic import op
import sqlalchemy as sa

revision = 'f773d24842da'
down_revision = '5048e99f2987'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "modules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"]),
    )
    op.create_index("ix_tasks_module_id", "tasks", ["module_id"])

def downgrade():
    op.drop_index("ix_tasks_module_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("modules")