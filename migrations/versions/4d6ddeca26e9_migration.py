"""migration

Revision ID: 4d6ddeca26e9
Revises: 
Create Date: 2025-02-20 03:22:11.715005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d6ddeca26e9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scraped_data', sa.Column('temp_token', sa.String(length=512), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scraped_data', 'temp_token')
    # ### end Alembic commands ###
