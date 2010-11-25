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

from repoze.what.predicates import NotAuthorizedError
from repoze.what.predicates import not_anonymous, has_permission

class Controller(object):
    @cherrypy.expose()
    @cherrypy.tools.render(template='gatherings.html')
    @cherrypy.tools.close_session()
    def index(self):
        debug = not_anonymous(msg='log in!')\
            .is_met(cherrypy.request.wsgi_environ)
        print "userid:", cherrypy.request.wsgi_environ.get('repoze.who.userid', None)
        identity = cherrypy.request.wsgi_environ.get('repoze.who.identity', None)
        print "identity:", dict(identity if identity else {})
        print "REMOTE_USER:", cherrypy.request.wsgi_environ.get('REMOTE_USER', None)
        try:
            not_anonymous(msg='log in!')\
                .check_authorization(cherrypy.request.wsgi_environ)
            #has_permission('new').check_authorization(cherrypy.request.wsgi_environ)
        except NotAuthorizedError, e:
            if 'repoze.who.identity' in cherrypy.request.wsgi_environ:
                print "forbidden"
                raise cherrypy.HTTPError(403, str(e)) # forbidden
            else:
                print "unauthorized"
                raise cherrypy.HTTPError(401, str(e)) # unauthorized
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

###############################################################################

from repoze.what.adapters import BaseSourceAdapter
from repoze.what.middleware import setup_auth
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.form import RedirectingFormPlugin

class MapAuthenticator(object):
    def __init__(self, users):
        self.users = users

    def authenticate(self, environ, identity):
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            return None
        if login in self.users and self.users[login] == password:
            return login
        return None

class DictGroupSource(BaseSourceAdapter):
    def __init__(self, sections):
        super(BaseSourceAdapter, self).__init__()
        self.sections = sections

    def _get_all_sections(self):
        return self.sections

    def _get_section_items(self, section):
        return self.sections[section]

    def _find_sections(self, credentials):
        id = credentials['repoze.who.userid']
        return set([key for key, value in self.sections.iteritems()
                if id in value])

    def _include_items(self, section, items):
        self.sections[section] |= items

    def _exclude_items(self, section, items):
        self.sections[section] -= items

    def _item_is_included(self, section, item):
        return item in self.sections[section]

    def _create_sectioin(self, section):
        self.sections[section] = set()

    def _edit_section(self, section, new_section):
        self.sections[new_section] = self.sections[section]
        del self.sections[section]

    def _delete_section(self, section):
        del self.sections[section]

    def _section_exists(self, section):
        return sectioin in self.sections

class DictPermissionSource(BaseSourceAdapter):
    def __init__(self, sections):
        super(BaseSourceAdapter, self).__init__()
        self.sections = sections

    def _get_all_sections(self):
        return self.sections

    def _get_section_items(self, section):
        return self.sections[section]

    def _find_sections(self, group_name):
        return set([key for key, value in self.sections.iteritems()
                if group_name in value])

    def _include_items(self, section, items):
        self.sections[section] |= items

    def _exclude_items(self, section, items):
        self.sections[section] -= items

    def _item_is_included(self, section, item):
        return item in self.sections[section]

    def _create_sectioin(self, section):
        self.sections[section] = set()

    def _edit_section(self, section, new_section):
        self.sections[new_section] = self.sections[section]
        del self.sections[section]

    def _delete_section(self, section):
        del self.sections[section]

    def _section_exists(self, section):
        return sectioin in self.sections


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

authenticators = [('mapauth', MapAuthenticator(user_dict))]

auth_app = setup_auth(app,
        groups,
        permissions,
        identifiers=identifiers,
        authenticators=authenticators,
        challengers=challengers,
        )
###############################################################################

cherrypy.tree.graft(auth_app, '/')
cherrypy.engine.start()
cherrypy.engine.block()
