#!/usr/bin/env python

import os
import db
import cherrypy
from db import get_session
from db import Gathering, SourceType, Ressource, Zone
from jinja2 import Environment, FileSystemLoader


def initialize_data():
    with get_session() as session:
        miner = SourceType('miner')
        botanist = SourceType('botanist')
        fisher = SourceType('fisher')
        session.add(miner)
        session.add(botanist)
        session.add(fisher)

        la_noscea = Zone('La Noscea')
        thanalan = Zone('Thanalan')
        the_black_shroud = Zone('The Black Shroud')
        session.add(la_noscea)
        session.add(thanalan)
        session.add(the_black_shroud)

        tiger_cod = Ressource('Tiger Cod')
        malm_kelp = Ressource('Malm Kelp')
        session.add(tiger_cod)
        session.add(malm_kelp)

        copper_ore = Ressource('Copper Ore')
        yellow_copper_ore = Ressource('Yellow Copper Ore')
        bone_chip = Ressource('Bone Chip')
        session.add(copper_ore)
        session.add(yellow_copper_ore)
        session.add(bone_chip)

        gatherings = (
                Gathering(source_type=miner,
                    source_grade=1,
                    source_level=2,
                    primary_weapon=True,
                    job_level=11,
                    zone=la_noscea,
                    ressource=bone_chip,
                    quantity=3),
                )
        for gathering in gatherings:
            session.add(gathering)

def template(template):
    def decorate(f):
        def execute(*args, **kwargs):
            result = f(*args, **kwargs)
            return env.get_template(template).render(result)
        return execute
    return decorate

class Controller(object):
    @cherrypy.expose
    @template('gatherings.html')
    def index(self):
        with get_session() as session:
            gatherings = session.query(Gathering).all()
            return {'gatherings': gatherings}

# setup database
#db_url = r'sqlite:///c:/temp/farming.db'
db_url = r'sqlite://'

db.bind(db_url)
initialize_data()

# setup template environment
env = Environment(loader=FileSystemLoader('templates'))

# start cherrypy
cherrypy.quickstart(Controller())
