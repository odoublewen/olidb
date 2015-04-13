import datetime
from oliapp import db
from sqlalchemy.sql import func, desc
from sqlalchemy import UniqueConstraint
from flask.ext.security import UserMixin, RoleMixin
from flask import abort


experiment_oligoset = db.Table(
    'experiment_oligoset',
    db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id')),
    db.Column('oligoset_id', db.Integer, db.ForeignKey('oligoset.id')))


benchtop_oligoset = db.Table(
    'benchtop_oligoset',
    db.Column('oliuser_id', db.Integer, db.ForeignKey('oliuser.id')),
    db.Column('oligoset_id', db.Integer, db.ForeignKey('oligoset.id')))


# class to hold gene_info file
class Gene(db.Model):
    __tablename__ = 'gene'
    id = db.Column(db.Integer, primary_key=True)
    accessions = db.relationship('Accession', backref='gene')

    geneid = db.Column(db.Integer(), nullable=False)                # GeneID
    taxid = db.Column(db.Integer(), nullable=False)                 # tax_id
    symbol = db.Column(db.String(64), nullable=False)               # Symbol
    symbolother = db.Column(db.String(64), nullable=True)           # Symbol_from_nomenclature_authority
    fullname = db.Column(db.String(256), nullable=True)             # Full_name_from_nomenclature_authority
    locustag = db.Column(db.String(64), nullable=True)              # LocusTag
    synonyms = db.Column(db.String(256), nullable=True)             # Synonyms
    dbxrefs = db.Column(db.String(64), nullable=True)               # dbXrefs
    chromosome = db.Column(db.String(16), nullable=True)            # chromosome
    map_location = db.Column(db.String(16), nullable=True)          # map_location
    description = db.Column(db.String(256), nullable=True)          # description
    type_of_gene = db.Column(db.String(256), nullable=True)         # type_of_gene
    nomenclature_status = db.Column(db.String(256), nullable=True)  # Nomenclature_status
    other_designations = db.Column(db.String(256), nullable=True)   # Other_designations
    modification_date = db.Column(db.String(256), nullable=True)    # Modification_date


# class to hold gene2accession file
class Accession(db.Model):
    __tablename__ = 'accession'
    id = db.Column(db.Integer, primary_key=True)
    gene_id = db.Column(db.Integer, db.ForeignKey('gene.id'))
    target = db.relationship('Target', backref='accession', uselist=False)

    status = db.Column(db.String(64), nullable=True)
    rna_acc = db.Column(db.String(16), nullable=True)            # RNA_nucleotide_accession.version
    rna_gi = db.Column(db.Integer(), nullable=True)              # RNA_nucleotide_gi
    matpeptide_acc = db.Column(db.String(16), nullable=True)     # mature_peptide_accession.version
    matpeptide_gi = db.Column(db.Integer(), nullable=True)       # mature_peptide_gi
    prot_acc = db.Column(db.String(16), nullable=True)           # protein_accession.version
    prot_gi = db.Column(db.Integer(), nullable=True)             # protein_gi
    genome_acc = db.Column(db.String(16), nullable=True)         # genomic_nucleotide_accession.version
    genome_gi = db.Column(db.Integer(), nullable=True)           # genomic_nucleotide_gi
    genome_start = db.Column(db.Integer(), nullable=True)        # start_position_on_the_genomic_accession
    genome_end = db.Column(db.Integer(), nullable=True)          # end_position_on_the_genomic_accession
    genome_orientation = db.Column(db.Boolean(), nullable=True)  # orientation
    genome_assembly = db.Column(db.String(16), nullable=True)    # assembly

    def __repr__(self):
        return '<%r %r>' % self.symbol, self.rna_acc


class Experiment(db.Model):
    __tablename__ = 'experiment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(256), nullable=True)
    date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    oligosets = db.relationship('Oligoset', secondary=experiment_oligoset,
                                backref=db.backref('experiments', lazy='dynamic'))
    oliuser_id = db.Column(db.Integer, db.ForeignKey('oliuser.id'), nullable=True)

    def __repr__(self):
        return '<%r>' % self.name


class Target(db.Model):
    __tablename__ = 'target'
    id = db.Column(db.Integer, primary_key=True)
    accession_id = db.Column(db.Integer, db.ForeignKey('accession.id'), nullable=True)
    oligosets = db.relationship('Oligoset', backref='target')

    taxonomy = db.Column(db.String(4), nullable=False)
    symbol = db.Column(db.String(64), nullable=False)
    namelong = db.Column(db.String(255), nullable=True)
    namealts = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<%s>' % self.symbol


class Oligoset(db.Model):
    __tablename__ = 'oligoset'
    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    oliuser_id = db.Column(db.Integer, db.ForeignKey('oliuser.id'), nullable=True)
    oligos = db.relationship('Oligo', backref='oligoset')

    tmid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(64), nullable=False, unique=True)
    date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    is_obsolete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<%s>' % self.name


def search_oligosets(session, term):

    return abort(404)


class Oligo(db.Model):
    __tablename__ = 'oligo'
    id = db.Column(db.Integer, primary_key=True)
    oligoset_id = db.Column(db.Integer, db.ForeignKey('oligoset.id'))

    oligoid = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.String(255), nullable=False)
    tubename = db.Column(db.String(64), nullable=False)
    probe = db.Column(db.String(16), nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    orderdate = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return self.tubename


class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer, primary_key=True)
    oliuser_id = db.Column(db.Integer, db.ForeignKey('oliuser.id'))
    rq_id = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    completed = db.Column(db.DateTime)


role_oliuser = db.Table(
    'role_oliuser',
    db.Column('oliuser_id', db.Integer(), db.ForeignKey('oliuser.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class OliUser(db.Model, UserMixin):
    __tablename__ = 'oliuser'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=role_oliuser)
    benchtop_oligosets = db.relationship('Oligoset', secondary=benchtop_oligoset)
    experiments = db.relationship('Experiment', backref='oliuser')
    jobs = db.relationship('Job', backref='oliuser')


class Primer3Settings(db.Model):
    __tablename__ = 'primer3settings'
    id = db.Column(db.Integer, primary_key=True)
    settings = db.Column(db.Text)
    oliuser_id = db.Column(db.Integer, db.ForeignKey('oliuser.id'))
