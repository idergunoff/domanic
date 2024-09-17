"""add piroliz reservoir

Revision ID: 5d2b188aa6d7
Revises: 
Create Date: 2024-09-16 16:26:27.413486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d2b188aa6d7'
down_revision: Union[str, None] = None
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

    op.create_table(
        'temp_data_piroliz_extr',
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

    op.execute('INSERT INTO temp_data_piroliz_extr ( '
               'id, depth, name, well_id, s1, s2, s3, s3_, s3co, s3_co, s4co2, s5, s4co, tmax, '
               'pc, rc, toc, pp, cmin, hi, s1_toc, oxminc, prminc, pi, oi, oico) '
               'SELECT '
               'id, depth, name, well_id, s1, s2, s3, s3_, s3co, s3_co, s4co2, s5, s4co, tmax, '
               'pc, rc, toc, pp, cmin, hi, s1_toc, oxminc, prminc, pi, oi, oico '
               'FROM data_piroliz_extr')

    op.drop_table('data_piroliz_kern')
    op.drop_table('data_piroliz_extr')

    op.rename_table('temp_data_piroliz_kern', 'data_piroliz_kern')
    op.rename_table('temp_data_piroliz_extr', 'data_piroliz_extr')


def downgrade() -> None:
    op.drop_column('data_piroliz_kern', 's1r_r')
    op.drop_column('data_piroliz_kern', 's2a_r')
    op.drop_column('data_piroliz_kern', 'oil_r')
    op.drop_column('data_piroliz_kern', 's2b_r')
    op.drop_column('data_piroliz_kern', 'tmax_r')
    op.drop_column('data_piroliz_kern', 's3_r')
    op.drop_column('data_piroliz_kern', 'pc_r')
    op.drop_column('data_piroliz_kern', 'rc_r')
    op.drop_column('data_piroliz_kern', 'toc_r')
    op.drop_column('data_piroliz_kern', 'cmin_r')
    op.drop_column('data_piroliz_kern', 'hi_r')
    op.drop_column('data_piroliz_kern', 'oi_r')
    op.drop_column('data_piroliz_kern', 'tpi_r')
    op.drop_column('data_piroliz_kern', 'nso_kero_r')
    op.drop_column('data_piroliz_kern', 'light_oil_r')
    op.drop_column('data_piroliz_kern', 'heavy_oil_r')
    op.drop_column('data_piroliz_kern', 'nso_kero_part_r')
    op.drop_column('data_piroliz_kern', 'osi_r')
    op.drop_column('data_piroliz_kern', 'api_index')

    op.drop_column('data_piroliz_extr', 's1r_r')
    op.drop_column('data_piroliz_extr', 's2a_r')
    op.drop_column('data_piroliz_extr', 'oil_r')
    op.drop_column('data_piroliz_extr', 's2b_r')
    op.drop_column('data_piroliz_extr', 'tmax_r')
    op.drop_column('data_piroliz_extr', 's3_r')
    op.drop_column('data_piroliz_extr', 'pc_r')
    op.drop_column('data_piroliz_extr', 'rc_r')
    op.drop_column('data_piroliz_extr', 'toc_r')
    op.drop_column('data_piroliz_extr', 'cmin_r')
    op.drop_column('data_piroliz_extr', 'hi_r')
    op.drop_column('data_piroliz_extr', 'oi_r')
    op.drop_column('data_piroliz_extr', 'tpi_r')
    op.drop_column('data_piroliz_extr', 'nso_kero_r')
    op.drop_column('data_piroliz_extr', 'light_oil_r')
    op.drop_column('data_piroliz_extr', 'heavy_oil_r')
    op.drop_column('data_piroliz_extr', 'nso_kero_part_r')
    op.drop_column('data_piroliz_extr', 'osi_r')
    op.drop_column('data_piroliz_extr', 'api_index')
