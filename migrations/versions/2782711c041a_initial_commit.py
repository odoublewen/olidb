"""initial commit

Revision ID: 2782711c041a
Revises: None
Create Date: 2015-11-22 05:55:11.542705

"""

# revision identifiers, used by Alembic.
revision = '2782711c041a'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oliuser',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('gene',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('geneid', sa.Integer(), nullable=False),
    sa.Column('taxid', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(length=64), nullable=False),
    sa.Column('symbolother', sa.String(length=64), nullable=True),
    sa.Column('fullname', sa.String(length=256), nullable=True),
    sa.Column('locustag', sa.String(length=64), nullable=True),
    sa.Column('synonyms', sa.String(length=256), nullable=True),
    sa.Column('dbxrefs', sa.String(length=64), nullable=True),
    sa.Column('chromosome', sa.String(length=16), nullable=True),
    sa.Column('map_location', sa.String(length=16), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('type_of_gene', sa.String(length=256), nullable=True),
    sa.Column('nomenclature_status', sa.String(length=256), nullable=True),
    sa.Column('other_designations', sa.String(length=256), nullable=True),
    sa.Column('modification_date', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('job',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jobname', sa.String(length=128), nullable=False),
    sa.Column('jobid', sa.String(length=64), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('numberdone', sa.Integer(), nullable=True),
    sa.Column('numbertotal', sa.Integer(), nullable=True),
    sa.Column('oliuser_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['oliuser_id'], ['oliuser.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('jobid')
    )
    op.create_table('experiment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('oliuser_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['oliuser_id'], ['oliuser.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('accession',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gene_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=64), nullable=True),
    sa.Column('rna_acc', sa.String(length=16), nullable=True),
    sa.Column('rna_gi', sa.Integer(), nullable=True),
    sa.Column('matpeptide_acc', sa.String(length=16), nullable=True),
    sa.Column('matpeptide_gi', sa.Integer(), nullable=True),
    sa.Column('prot_acc', sa.String(length=16), nullable=True),
    sa.Column('prot_gi', sa.Integer(), nullable=True),
    sa.Column('genome_acc', sa.String(length=16), nullable=True),
    sa.Column('genome_gi', sa.Integer(), nullable=True),
    sa.Column('genome_start', sa.Integer(), nullable=True),
    sa.Column('genome_end', sa.Integer(), nullable=True),
    sa.Column('genome_orientation', sa.Boolean(), nullable=True),
    sa.Column('genome_assembly', sa.String(length=16), nullable=True),
    sa.ForeignKeyConstraint(['gene_id'], ['gene.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role_oliuser',
    sa.Column('oliuser_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['oliuser_id'], ['oliuser.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], )
    )
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipename', sa.String(length=255), nullable=False),
    sa.Column('inner_recipe', sa.Text(), nullable=False),
    sa.Column('outer_recipe', sa.Text(), nullable=False),
    sa.Column('oliuser_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['oliuser_id'], ['oliuser.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('target',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('accession_id', sa.Integer(), nullable=True),
    sa.Column('taxonomy', sa.String(length=4), nullable=False),
    sa.Column('symbol', sa.String(length=64), nullable=False),
    sa.Column('namelong', sa.String(length=255), nullable=True),
    sa.Column('namealts', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['accession_id'], ['accession.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oligoset',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('target_id', sa.Integer(), nullable=True),
    sa.Column('oliuser_id', sa.Integer(), nullable=True),
    sa.Column('tmid', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.String(length=64), nullable=False),
    sa.Column('location', sa.String(length=64), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('is_obsolete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['oliuser_id'], ['oliuser.id'], ),
    sa.ForeignKeyConstraint(['target_id'], ['target.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('experiment_oligoset',
    sa.Column('experiment_id', sa.Integer(), nullable=True),
    sa.Column('oligoset_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['experiment_id'], ['experiment.id'], ),
    sa.ForeignKeyConstraint(['oligoset_id'], ['oligoset.id'], )
    )
    op.create_table('oligo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('oligoset_id', sa.Integer(), nullable=True),
    sa.Column('oligoid', sa.Integer(), nullable=True),
    sa.Column('sequence', sa.String(length=255), nullable=False),
    sa.Column('tubename', sa.String(length=64), nullable=False),
    sa.Column('probe', sa.String(length=16), nullable=True),
    sa.Column('comments', sa.String(length=255), nullable=True),
    sa.Column('orderdate', sa.DateTime(), nullable=True),
    sa.Column('tm', sa.Float(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['oligoset_id'], ['oligoset.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('benchtop_oligoset',
    sa.Column('oliuser_id', sa.Integer(), nullable=True),
    sa.Column('oligoset_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['oligoset_id'], ['oligoset.id'], ),
    sa.ForeignKeyConstraint(['oliuser_id'], ['oliuser.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('benchtop_oligoset')
    op.drop_table('oligo')
    op.drop_table('experiment_oligoset')
    op.drop_table('oligoset')
    op.drop_table('target')
    op.drop_table('recipe')
    op.drop_table('role_oliuser')
    op.drop_table('accession')
    op.drop_table('experiment')
    op.drop_table('job')
    op.drop_table('role')
    op.drop_table('gene')
    op.drop_table('oliuser')
    ### end Alembic commands ###