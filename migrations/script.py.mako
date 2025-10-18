"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision if down_revision else None}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa

revision = "${up_revision}"
down_revision = ${f"'{down_revision}'" if down_revision else "None"}
branch_labels = ${f"'{branch_labels}'" if branch_labels else "None"}
depends_on = ${f"'{depends_on}'" if depends_on else "None"}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
