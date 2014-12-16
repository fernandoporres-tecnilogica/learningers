# -*- coding: utf-8 -*-
from django.db import models
from simplemediawiki import MediaWiki
from catalog.models.base import ResourceLanguage, Resource, register_resource
from django.http import Http404
import re
from django.core.urlresolvers import reverse
from itertools import chain
import string
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _  
from django.utils.translation import ugettext_lazy as __
from django import template
from django.template.defaultfilters import stringfilter
from django.core.exceptions import ValidationError

register = template.Library()

def upper_repl(match):
    return match.group(1).upper()
 
@register.filter
@stringfilter
def wiki_deslugify(string):
    result = re.sub(r'[-_]', ' ', string)
    result = re.sub(r'^(\w)',upper_repl, result)
    return result
 
@register.filter
@stringfilter
def wiki_slugify(string):
    string = re.sub(r'^.+[:]','',string)
    string = re.sub(r'\s', '_', string)
    string = re.sub(r'^(\w)',upper_repl, string)
    return string

p = re.compile(r'href="/([^/"]+)/([^/"]+)"')

# Model representing a Mediawiki-powered wiki somewhere on the web
class Wiki(models.Model):
    MAIN_NAMESPACE = 0
    IMAGE_NAMESPACE = 6
    NAMESPACE_CHOICES = (
                          (MAIN_NAMESPACE, 'Articles'),
                          (IMAGE_NAMESPACE, 'Images'),
                          )
    NAMESPACE_TYPES = { MAIN_NAMESPACE: 'wiki', IMAGE_NAMESPACE:'linksgallery' }
    
    name = models.CharField(max_length=200, help_text=_(u'Nom sous lequel ce wiki est connu'))
    shortname = models.SlugField(max_length=50,help_text=_(u'Identifiant du wiki (charactères ASCII et chiffres seulement)'))
    url = models.URLField(help_text=_(u'Adresse du répertoire où se trouve api.php'))
    language = models.ForeignKey(ResourceLanguage)
    # the namespace we are interested in in this wiki
    namespace = models.IntegerField(choices=NAMESPACE_CHOICES,default=MAIN_NAMESPACE,help_text=_('Type de médias présents sur ce wiki'))
    # Resource slug
    slug = models.CharField(max_length=50,editable=False)
    
    def __init__(self,*args,**kwargs):
        super(Wiki,self).__init__(*args,**kwargs)
        self.wiki = MediaWiki(self.url + 'api.php')
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = self.shortname + '.' + self.language
        if not self.shortname:
            self.shortname = self.name
        super(Wiki,self).save(*args,**kwargs)
        
    def wiki_links_replacer(self,match):
        if match.group(1) == 'wiki':
            return 'href="' + reverse('catalog:wiki',kwargs={'slug':self.slug}) + match.group(2) + '"'
        elif match.group(1) == 'w':
            return 'href="' + self.url + match.group(2) + '" target="_blank"'
        else:
            return match.group()
         
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name
    
    # find out the actual page title after all redirections
    def get_redirect_title(self, title):
        # first see if there is a redirect
        test = self.wiki.call({'action':'query','redirects':'true','titles':title})
        if not 'query' in test:
            raise Http404
        if 'redirects' in test['query']: # a redirect was encountered
            return test['query']['redirects'][-1]['to']
        elif not 'pages' in test['query']: # no page was found
            return ''
        else:
            return title
                
    def slugify(self,title):
        return self.slug + '/' + wiki_slugify(title)
    
    @staticmethod
    def make_from_slug(slug):
        wiki_slug, slug = slug.split('/',1)
        title = wiki_deslugify(slug)
        wiki = get_object_or_404(Wiki,slug=wiki_slug)
        title,snippet = wiki.get_snippet(title)
        return wiki,title,snippet
        
    # Retrieve the whole content of a single page
    def get_page(self, title):
        # first see if the page exists
        test = self.wiki.call({'action':'query','redirects':'true','titles':title})
        if not 'pages' in test['query']: # no page was found
            raise Http404
        else:
            # yes, there is ! return special string to indicate it
            data = self.wiki.call({'action':'parse', 'page': title, 'prop':'text','disablepp':'true'}) # , 'redirects':'true'
            html = data['parse']['text']['*']
            # we need to replace internal links
            html = p.sub(self.wiki_links_replacer,html)
            return html
        
    # retrieve a snippet for a single page
    def get_snippet(self,title):
        data = self.wiki.call({'action':'query', 'list':'search','srsearch':title,'srprop':'snippet', 'srnamespace':"%d" % self.namespace,'srlimit':'1'})
        data = data['query']['search']
        # if we are searching imaging we need to retrieve the thumbnail URLs
        if not data:
            raise Http404
        else:
            return (data[0]['title'],data[0]['snippet'])

    @staticmethod
    def search_all_wikis(querystring,queryloc,language):
        # search on available wikis in the requested language
        wqs = Wiki.objects.filter(Q(namespace=Wiki.IMAGE_NAMESPACE) | Q(namespace=Wiki.MAIN_NAMESPACE,language__code=language))
        return chain.from_iterable([w.search(querystring) for w in wqs])
    @staticmethod
    def list_all_wikis(language):
        for wiki in Wiki.objects.filter(language__code=language).values('shortname'):
            yield wiki['shortname']
    
    def search(self,querystring):
        data = self.wiki.call({'action':'query', 'list':'search','srsearch':querystring,'srprop':'snippet', 'srnamespace':"%d" % self.namespace})
        data = data['query']['search']
        # if we are searching imaging we need to retrieve the thumbnail URLs
        print data
        if self.namespace is Wiki.IMAGE_NAMESPACE:
            titles = [ d['title'] for d in data ]
            pages = self.wiki.call({'action':'query', 'titles' : string.join(titles,'|'), 'prop':'imageinfo', 'iiprop':'url', 'iiurlwidth':'300'})
            urls = [ page['imageinfo'][0]['thumburl'] for page in pages['query']['pages'].values() ] 
            for idx,d in enumerate(data):
                description = "<img src='" + urls[idx] + "'/>"
                dummy,name = string.split(d['title'],':') 
                yield {'resource_type':Wiki.NAMESPACE_TYPES[Wiki.IMAGE_NAMESPACE], 'source': self.shortname, 'name': name, 'slug': self.slugify(name), 'description': description }
        else:
            for d in data:
                yield {'resource_type':Wiki.NAMESPACE_TYPES[Wiki.MAIN_NAMESPACE], 'source': self.shortname, 'name': d['title'], 'slug': self.slugify(d['title']), 'description': d['snippet'] }
        
    # retrieve the url of a given image, if it exists on the wiki, otherwise raise 404 error
    def get_image_info(self,name):
        pages = self.wiki.call({'action':'query', 'titles' : 'File:'+name, 'prop':'imageinfo', 'iiprop':'url', 'iiurlwidth':'300'})
        print pages
        if 'pages' in pages['query']:
            inf = pages['query']['pages'].itervalues().next()['imageinfo'][0]
            return inf['url'],inf['thumburl']
        else:
            raise Http404
        
class WikimediaHtmlResource(Resource):
    'Un article dans un Wiki fonctionnant sous Wikimedia, par exemple Wikipédia'
    resource_type = 'wiki'
    user_friendly_type = __('Article Wiki')
    wiki = models.ForeignKey(Wiki, verbose_name=__('Wiki d\'origine'))
    title = models.CharField(max_length=200, verbose_name =__('Titre d\'origine'))

    def clean(self):
        # check if an article with this title exists in the provided wiki
        new_title = self.wiki.get_redirect_title(self.title)
        if new_title is '':
            raise ValidationError(_('L\'article "' + self.title + '" n\'existe pas sur ' + self.wiki.name ))
        self.title = new_title
        super(WikimediaHtmlResource, self).clean()
    def save(self,*args,**kwargs):
        if not self.pk:
            self.slug = self.wiki.slugify(self.title)
            self.name = self.title
        super(WikimediaHtmlResource, self).save(*args,**kwargs)
    @staticmethod
    def make_from_slug(parent,slug):
        wiki,name,snippet = Wiki.make_from_slug(slug)
        return WikimediaHtmlResource(name=name,wiki=wiki,title=name,parent=parent,description=snippet)    
    def data(self):
        return {'wiki_html': self.wiki.get_page(self.title) }

register_resource(WikimediaHtmlResource)