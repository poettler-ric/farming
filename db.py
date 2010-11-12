#!/usr/bin/env python

from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, Boolean, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import mapper, relationship

db_url = r'sqlite:///c:/temp/farming.db'
clear = True

engine = create_engine(db_url)

metadata = MetaData(bind=engine)
Session = scoped_session(sessionmaker(bind=engine))

gathering_table = Table('gathering', metadata,
        Column('id', Integer, primary_key=True),
        Column('source_type_id', Integer, ForeignKey('source_type.id')),
        Column('source_grade', Integer),
        Column('source_level', Integer),
        Column('weapon_grade', Integer),
        Column('primary_weapon', Boolean),
        Column('job_level', Integer),
        Column('zone_id', Integer, ForeignKey('zone.id')),
        Column('ressource_id', Integer, ForeignKey('ressource.id')),
        Column('quantity', Integer),
        )

source_type_table = Table('source_type', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        )

ressource_table = Table('ressource', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        )

zone_table = Table('zone', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        )

class Gathering(object):
    def __init__(self,
            source_type=None,
            source_grade=1,
            source_level=1,
            weapon_grade=1,
            primary_weapon=True,
            job_level=1,
            zone=None,
            ressource=None,
            quantity=0,
            ):
        self.source_type = source_type
        self.source_grade = source_grade
        self.source_level = source_level
        self.primary_weapon = primary_weapon
        self.job_level = job_level
        self.zone = zone
        self.ressource = ressource
        self.quantity = quantity

    def __repr__(self):
        return u"<Gathering: type: %s grade: %s resource: %s quantity: %s>" \
                % (
                        self.source_type.name,
                        self.source_grade,
                        self.ressource.name,
                        self.quantity,
                        )

class SourceType(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return u"<SourceType: %s>" % self.name

class Ressource(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return u"<Ressource: %s>" % self.name

class Zone(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return u"<Zone: %s>" % self.name


mapper(Gathering, gathering_table, properties={
    'source_type': relationship(SourceType),
    'ressource': relationship(Ressource),
    'zone': relationship(Zone),
    })
mapper(SourceType, source_type_table)
mapper(Ressource, ressource_table)
mapper(Zone, zone_table)

if clear:
    metadata.drop_all()
metadata.create_all()
