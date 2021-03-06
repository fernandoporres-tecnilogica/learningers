# -*- coding: utf-8 -*-
""" 
Support for Sympa mailing lists.

This is not supported yet.
"""
from __future__ import unicode_literals

#!/usr/bin/env python

import requests
import re
from datetime import datetime
from lxml import etree
from catalog.models.base import Resource,register_resource
from django.db import models
from django.utils.translation import ugettext_lazy as __
from django.utils.translation import ugettext as _

class Sympa(models.Model):
    "A sympa server"
    url = models.URLField()
    
    def __init__(self, *args, **kwargs):
        self.session = requests.session(cookies=dict(sympalang='en_US'))
#        self.lists = {}
        super(Sympa,self).__init__(*args,**kwargs)

    def logged_in(self):
        return page_logged_in(self.get_page())

    def log_in(self, email, passwd):
        login = self.post_command(action='login', email=email, passwd=passwd)
        if not page_logged_in(login):
            raise RuntimeError('Authentication failure')
        self.__populate_lists(login)

    def log_out(self):
        self.post_command(action='logout')

    LISTS_XPATH = etree.XPath(
            '/html/body/div/div/div/ul[@class = "listenum"]/li/a/@href')
    
    def __populate_lists(self, page):
        root = get_page_root(page)
        links = self.LISTS_XPATH(root)
        self.lists = (link.rsplit('/', 1)[1] for link in links)
#        self.lists = dict((name, MailingList(self, name)) for name in names)

    def post_command(self, **kwargs):
        page = self.session.post(self.url, data=kwargs)
        return page

    def get_page(self, *params):
        uri = '{0}/{1}'.format(self.url, '/'.join(params))
        return self.session.get(uri)

def page_logged_in(page):
    return 'action_logout' in page.text

ENCODING_RE = re.compile(r'<meta[^>]+>| encoding="[^"]+"')
def get_page_root(page):
    return etree.HTML(ENCODING_RE.sub('', page.text))

LISTDIR_XPATH = etree.XPath(
    '/html/body/div/div/div[@id="Paint"]/div[@class="ContentBlock"]/table/tr')

class MailingList(Resource):
    "A sympa mailing list"
    sympa = models.ForeignKey(Sympa)
    listname = models.CharField(max_length=50)
    
    def __repr__(self):
        return '<MailingList "{0}">'.format(self.listname)

    def listdir(self, path='/'):
        page = self.sympa.get_page('d_read', self.listname, path)
        rows = LISTDIR_XPATH(get_page_root(page))
        return dict(row2entry(row) for row in rows[1:])

    def openfile(self, path):
        page = self.sympa.get_page('d_read', self.listname, path)
        return page.raw

TIME_FORMAT = '%d %b %Y'
NAME_XPATH = etree.XPath('td[position() = 1]/a/text()')
TD_XPATH = etree.XPath('td[position() = $pos]/text()')
def row2entry(row):
    name = ''.join(NAME_XPATH(row)).strip()
    timetext = ''.join(TD_XPATH(row, pos=4)).strip()
    updated = datetime.strptime(timetext, TIME_FORMAT).date()
    try:
        size = int(''.join(TD_XPATH(row, pos=3)).replace('.', ''))
        entry = File(name, updated, size)
    except ValueError:
        entry = Directory(name, updated)
    return (name, entry)

class Entry(object):
    def __init__(self, name, updated):
        self.name = name
        self.updated = updated

    def is_dir(self):
        raise NotImplementedError()
    
class File(Entry):
    def __init__(self, name, updated, size):
        Entry.__init__(self, name, updated)
        self.size = size

    def __repr__(self):
        return '<File "{0}" size={1} updated="{2}">'.format(
                self.name, self.size, self.updated)

    def is_dir(self):
        return False

class Directory(Entry):
    def __repr__(self):
        return '<Directory "{0}" updated="{1}">'.format(self.name, self.updated)

    def is_dir(self):
        return True

