"""add piroliz nop

Revision ID: d478b809878e
Revises: 5d2b188aa6d7
Create Date: 2024-09-17 10:48:13.376076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd478b809878e'
down_revision: Union[str, None] = '5d2b188aa6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'temp_data_piroliz_kern',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('depth', sa.Float()),
        sa.Column('name', sa.String()),
        sa.Column('well_id', sa.Integer(), sa.ForeignKey('wells.id')),
        sa.Column('s1', sa.Float()),
        sa.Column('s2', sa.Float()),
        sa.Column('s3', sa.Float()),
        sa.Column('s3_', sa.Float()),
        sa.Column('s3co', sa.Float()),
        sa.Column('s3_co', sa.Float()),
        sa.Column('s4co2', sa.Float()),
        sa.Column('s5', sa.Float()),
        sa.Column('s4co', sa.Float()),
        sa.Column('tmax', sa.Float()),

        sa.Column('pc', sa.Float()),
        sa.Column('rc', sa.Float()),
        sa.Column('toc', sa.Float()),
        sa.Column('pp', sa.Float()),
        sa.Column('cmin', sa.Float()),
        sa.Column('nop', sa.Float()),
        sa.Column('hi', sa.Float()),
        sa.Column('s1_toc', sa.Float()),
        sa.Column('oxminc', sa.Float()),
        sa.Column('prminc', sa.Float()),
        sa.Column('pi', sa.Float()),
        sa.Column('oi', sa.Float()),
        sa.Column('oico', sa.Float()),

        sa.Column('s1r_r', sa.Float()),
        sa.Column('s2a_r', sa.Float()),
        sa.Column('oil_r', sa.Float()),
        sa.Column('s2b_r', sa.Float()),
        sa.Column('tmax_r', sa.Float()),
        sa.Column('s3_r', sa.Float()),
        sa.Column('pc_r', sa.Float()),
        sa.Column('rc_r', sa.Float()),
        sa.Column('toc_r', sa.Float()),
        sa.Column('cmin_r', sa.Float()),
        sa.Column('hi_r', sa.Float()),
        sa.Column('oi_r', sa.Float()),
        sa.Column('tpi_r', sa.Float()),
        sa.Column('nso_kero_r', sa.Float()),
        sa.Column('light_oil_r', sa.Float()),
        sa.Column('heavy_oil_r', sa.Float()),
        sa.Column('nso_kero_part_r', sa.Float()),
        sa.Column('osi_r', sa.Float()),
        sa.Column('api_index', sa.Float())
        )

    op.execute('INSERT INTO temp_data_piroliz_kern ( '
               'id, depth, name, well_id, s1, s2, s3, s3_, s3co, s3_co, s4co2, s5, s4co, tmax, '
               'pc, rc, toc, pp, cmin, hi, s1_toc, oxminc, prminc, pi, oi, oico) '
               'SELECT '
               'id, depth, name, well_id, s1, s2, s3, s3_, s3co, s3_co, s4co2, s5, s4co, tmax, '
               'pc, rc, toc, pp, cmin, hi, s1_toc, oxminc, prminc, pi, oi, oico '
               'FROM data_piroliz_kern')

    op.drop_table('data_piroliz_kern')

    op.rename_table('temp_data_piroliz_kern', 'data_piroliz_kern')


def downgrade() -> None:
    op.drop_column('data_piroliz_kern', 'nop')