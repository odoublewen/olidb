import datetime
from oli import db


class Oligo(db.Model):
    __tablename__ = 'oligo'
    id = db.Column(db.Integer, primary_key=True)
    oligoset_id = db.Column(db.Integer, db.ForeignKey('oligo_set.id'), nullable=False)
    seq = db.Column(db.String(255), nullable=False)
    tubename = db.Column(db.String(255), nullable=False)
    probe = db.Column(db.String(255), nullable=False)
    comments = db.Column(db.String(255), nullable=False)
    orderdate = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Tubename %r>' % (self.tubename)


class OligoSet(db.Model):
    __tablename__ = 'oligo_set'
    id = db.Column(db.Integer, primary_key=True)
    setname = db.Column(db.String(255), nullable=False)


# def cleanslate():
#     conn = engine.connect()
#
#     # the transaction only applies if the DB supports
#     # transactional DDL, i.e. Postgresql, MS SQL Server
#     trans = conn.begin()
#     inspector = reflection.Inspector.from_engine(engine)
#
#     # gather all data first before dropping anything.
#     # some DBs lock after things have been dropped in
#     # a transaction.
#     metadata = MetaData()
#     tbs = []
#     all_fks = []
#     for table_name in inspector.get_table_names():
#         fks = []
#         for fk in inspector.get_foreign_keys(table_name):
#             if not fk['name']:
#                 continue
#             fks.append(
#                 ForeignKeyConstraint((),(),name=fk['name'])
#                 )
#         t = Table(table_name, metadata, *fks)
#         tbs.append(t)
#         all_fks.extend(fks)
#
#     for fkc in all_fks:
#         conn.execute(DropConstraint(fkc))
#
#     for table in tbs:
#         conn.execute(DropTable(table))
#
#     trans.commit()
#
#     Base.metadata.create_all(engine)
