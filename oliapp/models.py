import datetime
from oliapp import db
from lib.postgres import to_query_term, make_weighted_document_column
from sqlalchemy.sql import func, desc


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


experiment_design = db.Table(
    'experiment_design',
    db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id')),
    db.Column('design_id', db.Integer, db.ForeignKey('design.id'))
)


class Experiment(db.Model):
    __tablename__ = 'experiment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    folder = db.Column(db.String(16), nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    designs = db.relationship('Design', secondary=experiment_design, backref=db.backref('experiments', lazy='dynamic'))

    def __repr__(self):
        return '<Setname %r>' % self.setname

    # TODO: add properties, etc
    # @property
    # def length(self):
    #     return Experiment.designs()
    #
    # def __len__():
    #     pass


class Target(db.Model):
    __tablename__ = 'target'
    id = db.Column(db.Integer, primary_key=True)
    accession_id = db.Column(db.Integer, db.ForeignKey('accession.id'), nullable=True)
    designs = db.relationship('Design', backref='target')

    taxonomy = db.Column(db.String(4), nullable=False)
    genename = db.Column(db.String(64), nullable=False)
    targetnamelong = db.Column(db.String(255), nullable=True)
    targetnamealts = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<%s>' % self.genename


class Design(db.Model):
    __tablename__ = 'design'
    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    oligos = db.relationship('Oligo', backref='design')

    tmid = db.Column(db.Integer, nullable=False)
    designname = db.Column(db.String(64), nullable=False, unique=True)
    designdate = db.Column(db.DateTime, nullable=True)
    designer = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    is_public = db.Column(db.Boolean(), default=False)
    is_obsolete = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<%s>' % self.designname

    @classmethod
    def by_id(cls, designid):
        query = cls.query.get(designid)
        return query


def search_designs(session, term):

    # local_session = db.session.query(Target, Design).join(Design).session
    #
    # return local_session.query(Design.designname, Target.genename).join(Target).limit(20).all()
    # return db.session.query(Design, Target).join(Target).limit(20).all()

    term = to_query_term(term)

    search_subquery = session.query(
        Design.id.label('design_id'),
        make_weighted_document_column(
            [(Design.designname, 'A'),
             (Target.genename, 'A'),
             (Target.targetnamealts, 'A'),
             (Target.targetnamelong, 'B'),
             (Design.designer, 'B'),
             (Design.location, 'B')]).label('document')).join(Target).subquery()

    search_query = session.query(
        Design.id,
        Design.tmid,
        Design.designname,
        Design.designdate,
        Target.genename,
        Target.targetnamelong,
        Target.targetnamealts,
        func.ts_rank(search_subquery.c.document, func.to_tsquery(term)))\
        .join(Target)\
        .join(search_subquery, Design.id == search_subquery.c.design_id)\
        .filter(search_subquery.c.document.match(term))\
        .order_by(desc(func.ts_rank(search_subquery.c.document,func.to_tsquery(term))))

    return search_query.all()

    # # support reassignment through lists
    # results = [[rank, did, dname, ddate, designer, pub, obs] for
    #            rank, did, dname, ddate, designer, pub, obs in search_query.all()]
    #
    # return sorted(results, key=operator.itemgetter(0))[::-1]


class Oligo(db.Model):
    __tablename__ = 'oligo'
    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey('design.id'))

    oligoid = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.String(255), nullable=False)
    tubename = db.Column(db.String(64), nullable=False)
    probe = db.Column(db.String(16), nullable=True)
    comments = db.Column(db.String(255), nullable=True)
    orderdate = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return self.tubename


