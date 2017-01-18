from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# class to hold gene_info file
class Annotation(models.Model):
    geneid = models.IntegerField(null=False)                           # GeneID
    taxid = models.IntegerField(null=False)                            # tax_id
    symbol = models.CharField(max_length=64, null=False)               # Symbol
    symbolother = models.CharField(max_length=64, null=True)           # Symbol_from_nomenclature_authority
    fullname = models.CharField(max_length=256, null=True)             # Full_name_from_nomenclature_authority
    locustag = models.CharField(max_length=64, null=True)              # LocusTag
    synonyms = models.CharField(max_length=256, null=True)             # Synonyms
    dbxrefs = models.CharField(max_length=64, null=True)               # dbXrefs
    chromosome = models.CharField(max_length=16, null=True)            # chromosome
    map_location = models.CharField(max_length=16, null=True)          # map_location
    description = models.CharField(max_length=256, null=True)          # description
    type_of_gene = models.CharField(max_length=256, null=True)         # type_of_gene
    nomenclature_status = models.CharField(max_length=256, null=True)  # Nomenclature_status
    other_designations = models.CharField(max_length=256, null=True)   # Other_designations
    modification_date = models.CharField(max_length=256, null=True)    # Modification_date

    def __str__(self):
        return self.symbol


# class to hold gene2accession file
class Accession(models.Model):
    annotation = models.ForeignKey(Annotation, null=True)

    status = models.CharField(max_length=64, null=True)
    rna_acc = models.CharField(max_length=16, null=True)                # RNA_nucleotide_accession.version
    rna_gi = models.IntegerField(null=True)                             # RNA_nucleotide_gi
    matpeptide_acc = models.CharField(max_length=16, null=True)         # mature_peptide_accession.version
    matpeptide_gi = models.IntegerField(null=True)                      # mature_peptide_gi
    prot_acc = models.CharField(max_length=16, null=True)               # protein_accession.version
    prot_gi = models.IntegerField(null=True)                            # protein_gi
    genome_acc = models.CharField(max_length=16, null=True)             # genomic_nucleotide_accession.version
    genome_gi = models.IntegerField(null=True)                          # genomic_nucleotide_gi
    genome_start = models.IntegerField(null=True)                       # start_position_on_the_genomic_accession
    genome_end = models.IntegerField(null=True)                         # end_position_on_the_genomic_accession
    genome_orientation = models.NullBooleanField()                      # orientation
    genome_assembly = models.CharField(max_length=16, null=True)        # assembly

    def __str__(self):
        return self.rna_acc


class Gene(models.Model):
    accession = models.ForeignKey(Accession, null=True)

    taxonomy = models.CharField(max_length=4, null=False)
    symbol = models.CharField(max_length=64, null=False)
    namelong = models.CharField(max_length=255, null=True)
    namealts = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.symbol


class Oligoset(models.Model):
    gene = models.ForeignKey(Gene)
    user = models.ForeignKey(User, null=True)

    tmid = models.IntegerField(null=True)
    name = models.CharField(max_length=64, null=False, unique=True)
    date = models.DateTimeField(null=True)
    notes = models.CharField(max_length=64, null=False)
    location = models.CharField(max_length=64, null=False)
    is_public = models.BooleanField(default=False)
    is_obsolete = models.BooleanField(default=False)

    def __repr__(self):
        return '<%s>' % self.name

    def get_recent(n=10):
        return Oligoset.objects.exclude(date__isnull=True).order_by('-date')[:n]


class Oligo(models.Model):
    oligoset = models.ForeignKey(Oligoset)

    oligoid = models.IntegerField(null=True)
    sequence = models.CharField(max_length=255, null=False)
    tubename = models.CharField(max_length=64, null=False)
    probe = models.CharField(max_length=16, null=True)
    comments = models.CharField(max_length=255, null=True)
    orderdate = models.DateTimeField(null=True)
    tm = models.FloatField(null=True)
    created = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return self.tubename


class Experiment(models.Model):
    oligosets = models.ManyToManyField(Oligoset)
    user = models.ForeignKey(User, null=True)

    name = models.CharField(max_length=128, null=False, unique=True)
    description = models.CharField(max_length=256, null=True)
    date = models.DateTimeField(null=True, default=timezone.now)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_recent(n=10):
        return Experiment.objects.exclude(date__isnull=True).order_by('-date')[:n]


class Job(models.Model):
    jobname = models.CharField(max_length=128, null=False)
    jobid = models.CharField(max_length=64, unique=True, null=False)
    created = models.DateTimeField(default=timezone.now)
    numberdone = models.IntegerField()
    numbertotal = models.IntegerField()
    user = models.ForeignKey(User)


class Recipe(models.Model):
    recipename = models.CharField(max_length=255, unique=False, null=False)
    inner_recipe = models.TextField(null=False)
    outer_recipe = models.TextField(null=False)
    user = models.ForeignKey(User, null=True)







# role_oliuser = db.Table(
#     'role_oliuser',
#     db.Column('oliuser_id', db.Integer(), db.ForeignKey('oliuser.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))
#
#
# class Role(db.Model, RoleMixin):
#     __tablename__ = 'role'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = models.CharField(max_length=80), unique=True)
#     description = models.CharField(max_length=255))
#
#
# class OliUser(db.Model, UserMixin):
#     __tablename__ = 'oliuser'
#     id = db.Column(db.Integer, primary_key=True)
#     name = models.CharField(max_length=255), unique=False)
#     email = models.CharField(max_length=255), unique=True)
#     password = models.CharField(max_length=255))
#     active = db.Column(db.Boolean())
#     confirmed_at = db.Column(db.DateTime())
#     roles = db.relationship('Role', secondary=role_oliuser)
#     benchtop_oligosets = db.relationship('Oligoset', secondary=benchtop_oligoset)
#     experiments = db.relationship('Experiment', backref='oliuser')
#     jobs = db.relationship('Job', backref='oliuser')
#     recipes = db.relationship('Recipe', backref='oliuser')
#

