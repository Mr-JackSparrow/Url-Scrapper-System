"""migration

Revision ID: dc2736ea5a3d
Revises: 53987a40969c
Create Date: 2025-02-19 05:52:36.918194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc2736ea5a3d'
down_revision: Union[str, None] = '53987a40969c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scraped_data', sa.Column('user_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'scraped_data', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('scraped_data', 'email_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scraped_data', sa.Column('email_id', sa.VARCHAR(length=512), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'scraped_data', type_='foreignkey')
    op.drop_column('scraped_data', 'user_id')
    # ### end Alembic commands ###
