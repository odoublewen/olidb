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
        return '<Tubename %r>' % self.tubename


class OligoSet(db.Model):
    __tablename__ = 'oligo_set'
    id = db.Column(db.Integer, primary_key=True)
    setname = db.Column(db.String(255), nullable=False)

