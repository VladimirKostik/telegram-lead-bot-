"""normalize public number index

Revision ID: e0f06859f146
Revises: 1e8d1d635706
Create Date: 2026-09-16 00:59:16.172693

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e0f06859f146"
down_revision: Union[str, Sequence[str], None] = "1e8d1d635706"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Normalize the public_number index name."""

    op.execute(
        """
        ALTER INDEX IF EXISTS public.applications_public_number_key
        RENAME TO ix_applications_public_number
        """
    )


def downgrade() -> None:
    """Restore the previous public_number index name."""

    op.execute(
        """
        ALTER INDEX IF EXISTS public.ix_applications_public_number
        RENAME TO applications_public_number_key
        """
    )