# -*- coding: utf-8 -*-
"""
Support for external syndication feeds as resources,
using the feedparser python library. 
"""
from __future__ import unicode_literals

from django.db import models
from catalog.models.base import ResourceLanguage, Resource, register_resource, register_annotation_range
from feedparser import parse
from django.utils.text import slugify 
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _  
from django.utils.translation import ugettext_lazy as __
from urlparse import urlparse
import datetime

class Feed(Resource):
    'An external syndication feed, in any format supported by feedparser'
    url = models.URLField(verbose_name=__('Lien du flux'),help_text=__('Exemple: http://rawrfeminista.wordpress.com/feed/'))
    class Meta:
        verbose_name = __(u"Flux")
        verbose_name_plural = __(u"Flux")
    @property             
    def feed(self):
        if hasattr(self,'_feed'):
            return self._feed
        # check if the feed is valid
        d = parse(self.url)
        if not hasattr(d,'feed') or not 'title' in d.feed:
            raise ValidationError(_('Flux invalide'))
        self._feed = d.feed
        return d.feed
    @property  
    def entries(self):
        if hasattr(self,'_entries'):
            return self._entries
        d = parse(self.url)
        if not hasattr(d,'entries'):
            return []
        else:
            u2 = urlparse(self.url)
            for e in d.entries:
                if not(hasattr(e,'link')):
                    continue
                u1 = urlparse(e.link)
                e['feedentry_url'] = self.parent.get_absolute_url() + 'feedentry/' + u2.netloc + u1.path + u1.query
                e['datetime'] = datetime.datetime(*e['published_parsed'][:6])
            self._entries = d.entries
            return d.entries
    @property
    def title(self):
        return self.feed.title
    def clean(self):
        self.feed
        return super(Feed, self).clean()
    def set_defaults(self):
        if not self.name:
            self.name = self.feed.title
        if not self.description:
            if 'description' in self.feed:
                self.description = self.feed['description']
    def save(self,*args,**kwargs):
        if not self.pk:
            u = urlparse(self.url)
            self.slug = u.netloc + u.path + u.params + u.query
        self.set_defaults()            
        super(Feed, self).save(*args,**kwargs)  
    def preview(self):
        #print self.feed
        #if 'image' in self.feed and 'href'  in self.feed['image']:
        #    return "<img src='" + self.feed['image']['href'] + "'/>"
        if not self.description:
            if 'description' in self.feed:
                return self.feed['description']
        return self.description
    @staticmethod
    def make_from_slug(parent,slug):
        'Construct field from its slug'
        ret = Feed(parent=parent,url="http://" + slug)
        ret.set_defaults()
        return ret
  
class FeedEntry(Resource):
    'An entry in an external syndication feed, in any format supported by feedparser'
    url = models.URLField(verbose_name=__('URL du flux'),help_text=__("L'URL du flux, par exemple http://ensortantdelecole.wordpress.com/feed/"))
    link = models.CharField(max_length=2048,verbose_name=__('Chemin de l\'article'),help_text=__("Le chemin de l'article, tel qu'il est présenté dans le flux, par exemple /2015/03/03/abrogation-de-la-circulaire-chatel-circulaire-n-2012-056-du-27-3-2012/"))
    class Meta:
        verbose_name = __(u"Entrée de flux")
        verbose_name_plural = __(u"Entrées de flux")
    @property  
    def entry(self):
        if hasattr(self,'_entry'):
            return self._entry
        d = parse(self.url)
        if not hasattr(d,'entries'):
            raise ValidationError(_('Flux invalide'))
        print "self.link : %s" % self.link
        for e in d.entries:
            if not(hasattr(e,'link')):
                raise ValidationError(_('Lien introuvable dans le flux'))
            print "link : %s" % e.link
            if self.link in e.link:
                if not 'content' in e:
                    raise ValidationError(_('Contenu introuvable dans le flux'))
                if not 'title' in e:
                    raise ValidationError(_('Titre du contenu introuvable dans le flux'))
                if len(e.content) < 1:
                    raise ValidationError(_('Contenu introuvable dans le flux'))
                if not 'value' in e.content[0]:
                    raise ValidationError(_('Contenu introuvable dans le flux'))
                self._entry = e
                return e         
        raise ValidationError(_('Aucune entrée avec cette URL trouvée dans le flux'))
    @property
    def feed(self):
        if hasattr(self,'_feed'):
            return self._feed
        # check if the feed is valid
        d = parse(self.url)
        if not hasattr(d,'feed') or not 'title' in d.feed:
            raise ValidationError(_('Flux invalide'))
        self._feed = d.feed
        return d.feed
    def clean(self):
        self.entry
        return super(FeedEntry, self).clean()
    @property
    def title(self):
        return self.entry.title
    def set_defaults(self):
        if not self.name:
            self.name = self.entry.title
        if not self.description:
            if 'description' in self.entry:
                self.description = self.entry['description']            
    def save(self,*args,**kwargs):
        if not self.pk:
            u = urlparse(self.url)
            self.slug = u.netloc + self.link 
        self.set_defaults()
        super(FeedEntry, self).save(*args,**kwargs)  
    def data(self):
        return {'html': self.entry.content[0].value }
    def preview(self):
        if not self.description:
            if 'description' in self.entry:
                return self.entry['description']
        return self.description
    @staticmethod
    def make_from_slug(parent,slug):
        'Construct field entry from its slug'
        # First we need to figure out the feed URL from the permalink.
        u = urlparse("http://" + slug)
        if('wordpress' in u.netloc or 'noblogs' in u.netloc):
            url = "http://" + u.netloc + "/feed/"
        elif('blogspot' in u.netloc):
            url = "http://" + u.netloc + "/feeds/posts/default"
        elif('spip' in u.path):
            url = "http://" + u.netloc + "/spip.php?page=backend"
        elif('/?p=' in slug):
            url = "http://" + u.netloc + "/?feed=rss2"
        else:
            raise ValidationError(_("Impossible de reconstruire l'adresse du flux correspondant à l'article http://" + slug ))
        ret = FeedEntry(parent=parent,url=url,link=(u.path + u.query))
        ret.set_defaults()
        return ret
  
register_resource(Feed)        
register_resource(FeedEntry)