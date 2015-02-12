#!/usr/bin/env python
#
import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, DateTime, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint
import json

Base = declarative_base()


class Oligo(Base):
    __tablename__ = 'oligo'
    id = Column(Integer, primary_key=True)
    oligoset_id = Column(Integer, ForeignKey('oligo_set.id'), nullable=False)
    seq = Column(String(255), nullable=False)
    tubename = Column(String(255), nullable=False)
    probe = Column(String(255), nullable=False)
    comments = Column(String(255), nullable=False)
    orderdate = Column(DateTime, nullable=True)
    created = Column(DateTime, default=datetime.datetime.now)


class OligoSet(Base):
    __tablename__ = 'oligo_set'
    id = Column(Integer, primary_key=True)
    setname = Column(String(255), nullable=False)


def cleanslate():
    conn = engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()
    inspector = reflection.Inspector.from_engine(engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()
    tbs = []
    all_fks = []
    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                ForeignKeyConstraint((),(),name=fk['name'])
                )
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()

    Base.metadata.create_all(engine)
