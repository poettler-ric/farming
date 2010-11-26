#!/usr/bin/env python

from repoze.what.adapters import BaseSourceAdapter

class DictAuthenticator(object):
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
