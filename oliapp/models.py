import datetime
from oliapp import db


# class to hold gene_info file
class Gene(db.Model):
    __tablename__ = 'gene'
    id = db.Column(db.Integer, primary_key=True)
    accessions = db.relationship('Accession', backref='gene', lazy='dynamic')

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
    target = db.relationship('Target', backref='accession', uselist=False)
    gene_id = db.Column(db.Integer, db.ForeignKey('gene.id'))
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


class Target(db.Model):
    __tablename__ = 'target'
    id = db.Column(db.Integer, primary_key=True)
    accession_id = db.Column(db.Integer, db.ForeignKey('accession.id'))
    designs = db.relationship('Design', backref='target', lazy='dynamic')
    targetnamelong = db.Column(db.String(255), nullable=True)
    targetnamealts = db.Column(db.String(255), nullable=True)


designset_design = db.Table(
    'designset_design',
    db.Column('designset_id', db.Integer, db.ForeignKey('designset.id')),
    db.Column('design_id', db.Integer, db.ForeignKey('design.id'))
)


class Designset(db.Model):
    __tablename__ = 'designset'
    id = db.Column(db.Integer, primary_key=True)
    setname = db.Column(db.String(255), nullable=False)
    setdate = db.Column(db.DateTime, nullable=True)
    designs = db.relationship('Design', secondary=designset_design, backref=db.backref('designsets', lazy='dynamic'))

    def __repr__(self):
        return '<Setname %r>' % self.setname


class Design(db.Model):
    __tablename__ = 'design'
    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'))
    designname = db.Column(db.String(255), nullable=False, unique=True)
    oligos = db.relationship('Oligo', backref='design', lazy='dynamic')

    def __repr__(self):
        return '<Design name %r>' % self.name


class Oligo(db.Model):
    __tablename__ = 'oligo'
    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey('design.id'))
    seq = db.Column(db.String(255), nullable=False)
    tubename = db.Column(db.String(255), nullable=False)
    probe = db.Column(db.String(255), nullable=False)
    comments = db.Column(db.String(255), nullable=False)
    orderdate = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Tubename %r>' % self.tubename


