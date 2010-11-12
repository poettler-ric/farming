#!/usr/bin/env python

import cherrypy
from db import Session
from db import Gathering, SourceType, Ressource, Zone
from jinja2 import Environment, FileSystemLoader


def initialize_data():
    miner = SourceType('miner')
    botanist = SourceType('botanist')
    fisher = SourceType('fisher')
    Session.add(miner)
    Session.add(botanist)
    Session.add(fisher)

    la_noscea = Zone('La Noscea')
    thanalan = Zone('Thanalan')
    the_black_shroud = Zone('The Black Shroud')
    Session.add(la_noscea)
    Session.add(thanalan)
    Session.add(the_black_shroud)

    tiger_cod = Ressource('Tiger Cod')
    malm_kelp = Ressource('Malm Kelp')
    Session.add(tiger_cod)
    Session.add(malm_kelp)

    copper_ore = Ressource('Copper Ore')
    yellow_copper_ore = Ressource('Yellow Copper Ore')
    bone_chip = Ressource('Bone Chip')
    Session.add(copper_ore)
    Session.add(yellow_copper_ore)
    Session.add(bone_chip)

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
        Session.add(gathering)
    Session.commit()

def template(template):
    def decorate(f):
        def execute(*args, **kwargs):
            result = f(*args, **kwargs)
            return env.get_template(template).render(result)
        return execute
    return decorate

def close_session():
    Session.close()

cherrypy.tools.close_session = cherrypy.Tool('before_finalize', close_session)

class Controller(object):
    @cherrypy.expose()
    @template('gatherings.html')
    @cherrypy.tools.close_session()
    def index(self):
        gatherings = Session.query(Gathering).all()
        return {'gatherings': gatherings}

# fill the db with initial data
initialize_data()

# setup template environment
env = Environment(loader=FileSystemLoader('templates'))

# start cherrypy
cherrypy.config.update({
    #'tools.close_session.on': True,
    })
cherrypy.tree.mount(Controller(), '/')
cherrypy.engine.start()
cherrypy.engine.block()
