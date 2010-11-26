#!/usr/bin/env python

from db import Gathering, SourceType, Ressource, Zone
from db import Session
from jinja2 import Environment, FileSystemLoader
from repoze.what.middleware import setup_auth
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.predicates import NotAuthorizedError
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.form import RedirectingFormPlugin
from security import DictAuthenticator, DictGroupSource, DictPermissionSource
import cherrypy


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

def close_session():
    Session.close()

cherrypy.tools.close_session = cherrypy.Tool('before_finalize', close_session)

def render_template(template=None):
    oldhandler = cherrypy.request.handler
    def render(*args, **kwargs):
        result = oldhandler(*args, **kwargs)
        return env.get_template(template).render(result)
    cherrypy.request.handler = render

cherrypy.tools.render = cherrypy.Tool('before_handler', render_template)

def permission(predicate=None):
    oldhandler = cherrypy.request.handler
    def check_permission(*args, **kwargs):
        environment = cherrypy.request.wsgi_environ
        identity = environment.get('repoze.who.identity', None)
        try:
            #print dict(identity if identity else {})
            predicate.check_authorization(environment)
            result = oldhandler(*args, **kwargs)
            return result
        except NotAuthorizedError as e:
            if identity: # not authorized
                raise cherrypy.HTTPError(403, str(e))
            else: # not authenticated
                raise cherrypy.HTTPError(401, str(e))
    cherrypy.request.handler = check_permission

cherrypy.tools.permission = cherrypy.Tool('before_handler', permission)

class Controller(object):
    @cherrypy.expose()
    @cherrypy.tools.render(template='gatherings.html')
    @cherrypy.tools.permission(predicate=not_anonymous(msg='log in!'))
    @cherrypy.tools.close_session()
    def index(self):
        debug = not_anonymous(msg='log in!')\
            .is_met(cherrypy.request.wsgi_environ)
        gatherings = Session.query(Gathering).all()
        return {'gatherings': gatherings, 'debug': debug}

    @cherrypy.expose()
    @cherrypy.tools.render(template='login.html')
    def login(self, *args, **kwargs):
        return kwargs

    @cherrypy.expose()
    def do_login(self, *args, **kwargs):
        return "do_login"

    @cherrypy.expose()
    def do_logout(self, *args, **kwargs):
        return "do_logout"

# fill the db with initial data
initialize_data()

# setup template environment
env = Environment(loader=FileSystemLoader('templates'))

# start cherrypy
cherrypy.config.update({
    #'tools.close_session.on': True,
    })
app = cherrypy.Application(Controller())

# setup the security
user_dict = {
    'richi': 'richi',
    'chrissi': 'chrissi',
    'ulli': 'ulli',
    'steffi': 'steffi',
}

group_dict = {
    'male': set(['richi']),
    'older': set(['richi', 'chrissi']),
}

permission_dict = {
    'new': set(),
    'edit': set(['older']),
    'delete': set(['male', 'older']),
}

groups = {'all_groups': DictGroupSource(group_dict)}
permissions = {'all_permissions': DictPermissionSource(permission_dict)}

cookieident = AuthTktCookiePlugin('mySuperSecretSecret')

formauth = RedirectingFormPlugin('/login',
        '/do_login',
        '/do_logout',
        rememberer_name='cookieident')
identifiers = [('formauth', formauth), ('cookieident', cookieident)]
challengers = [('formauth', formauth)]

authenticators = [('mapauth', DictAuthenticator(user_dict))]

auth_app = setup_auth(app,
        groups,
        permissions,
        identifiers=identifiers,
        authenticators=authenticators,
        challengers=challengers,
        )

# mount the application
cherrypy.tree.graft(auth_app, '/')
cherrypy.engine.start()
cherrypy.engine.block()
