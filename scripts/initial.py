# -*- coding: utf-8 -*-
from catalog import models
from django.contrib.auth.models import User
from django.utils.translation import activate
from datetime import datetime
from schedule.models import Rule, Event
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, HOURLY, MINUTELY, SECONDLY
from django_mailman.models import List

def make_from_slug(model,parent,slug):
	if not model.objects.filter(slug=slug).exists():
		try:
			o = model.make_from_slug(parent,slug)
			o.full_clean()
			o.save()
			return o
		except:
			print 'Could not create ' + model.__name__ + ' source'
	else:
		return model.objects.get(slug=slug)

def run():
	# create languages
	fr,created = models.ResourceLanguage.objects.get_or_create(code='fr')
	en,created = models.ResourceLanguage.objects.get_or_create(code='en')
	activate('fr')

	# install locations 
	berlin,created = models.GeoLocation.objects.get_or_create(address='Berlin')
	thbm,created = models.GeoLocation.objects.get_or_create(address='Wallstraße 32, Berlin')
	nicol,created = models.GeoLocation.objects.get_or_create(address='90 chemin de Nicol, Toulouse, France')
	stpierre,created = models.GeoLocation.objects.get_or_create(address='Place Saint-Pierre, Toulouse, France')
	lejeune,created = models.GeoLocation.objects.get_or_create(address='16 rue Lejeune, Toulouse')

	# create parcours
	menagerie,created = models.Way.objects.get_or_create(name=u'La ménagerie', description=u'Plate-forme du théâtre francophone à Berlin')
	fnc,created = models.Way.objects.get_or_create(name=u'Foot not cops', description=u'Cantine autonome à Toulouse')
	enscene,created = models.Way.objects.get_or_create(parent=menagerie,name=u'En Scène', description=u'Atelier de théâtre')
	impro,created = models.Way.objects.get_or_create(parent=menagerie,name=u'I.M.P.R.O.', description=u'Atelier d\'improvisation théâtrale')
	revo,created = models.Way.objects.get_or_create(name=u'La révolution Russe',description=u'Documentation sur la révolution russe')
	gaset,created = models.Way.objects.get_or_create(name=u'GASET',description=u"Un groupement d'achat")
	# install some human sources
	lulu,created = User.objects.get_or_create(username=u'lulu',password='x',email=u'lulu@lili.org',first_name=u'Lucie',last_name=u'Rivallant-Delabie')
	romain,created = User.objects.get_or_create(username=u'linux2400',password='x',email=u'lulu@lili.org',first_name=u'Romain',last_name=u'Nguyen van yen')
	damien,created = models.HumanResource.objects.get_or_create(name=u'Damien Poinsard', description=u'Theaterpedagog', geo=berlin, parent=enscene)
	marjo,created = models.HumanResource.objects.get_or_create(name=u'Marjorie Nadal', description=u'Theaterpedagogin', geo=berlin, parent=impro)

	# create some recurrence rules
	daily,created = Rule.objects.get_or_create(name='Quotidienne',description=u'Répétition quotidienne',frequency='DAILY')
	weekly,created = Rule.objects.get_or_create(name='Hebdomadaire',description=u'Répétition hebdomadaire',frequency='WEEKLY')
	monthly,created = Rule.objects.get_or_create(name='Mensuelle',description=u'Répétition mensuelle',frequency='MONTHLY')

	# create some events
	x1,created = models.MeetingResource.objects.get_or_create(parent=enscene,name=u'En Scène 2012-2013, Ubu Roi',description=u'Atelier en Scène 2012-2013. Mise en scène de la pièce UBU ROI d\'Alfred Jarry',geo=thbm,start=datetime(2012, 10, 11, 20, 00, 00),end=datetime(2012, 10, 11, 22, 00, 00),rule=weekly)
	if(created):
		x1.participants.add(lulu)
		x1.participants.add(romain)
	x1,created = models.MeetingResource.objects.get_or_create(parent=fnc,name=u'Distribution',description=u'',geo=stpierre,start=datetime(2014, 12, 14, 17, 30, 00),end=datetime(2014, 12, 14, 20, 00, 00),rule=weekly)
	if(created):
		x1.participants.add(romain)
	x1,created = models.MeetingResource.objects.get_or_create(parent=fnc,name=u'Cuisine',description=u'',geo=lejeune,start=datetime(2014, 12, 14, 13, 00, 00),end=datetime(2014, 12, 14, 17, 30, 00),rule=weekly)
	if(created):
		x1.participants.add(romain)
	# add some wikis
	models.Wiki.objects.get_or_create(name=u'Wikipédia francophone',url='http://fr.wikipedia.org/w/',slug='wikipedia.fr',language=fr)
	models.Wiki.objects.get_or_create(name=u'English Wikipedia',url='http://en.wikipedia.org/w/',slug='wikipedia.com',language=en)
	models.Wiki.objects.get_or_create(name=u'English Wikihow',url='http://www.wikihow.com/',slug='wikihow.com',language=en)
	models.Wiki.objects.get_or_create(name=u'Wikihow francophone',url='http://fr.wikihow.com/',slug='wikihow.fr',language=fr)
	models.Wiki.objects.get_or_create(name=u'Wikiversity',url='http://en.wikiversity.org/w/',slug='wikiversity.com',language=en)
	models.Wiki.objects.get_or_create(name=u'Wikiversité',url='http://fr.wikiversity.org/w/',slug='wikiversity.fr',language=fr)

	# install some wiki sources
	make_from_slug(models.WikimediaHtmlResource,enscene,'wikipedia.com/Ubu_Roi')
	make_from_slug(models.WikimediaHtmlResource,enscene,'wikipedia.fr/Ubu_Roi')

	# install some mailing lists
	mailing,created=models.MailmanResource.objects.get_or_create(name=u'Mailing list de GASET', listname='g.a.s.e.t', password='73Vadziom!', email='g.a.s.e.t@listes.cooperative-integrale-toulouse.org',main_url='http://listes.cooperative-integrale-toulouse.org', encoding='iso-8859-1',parent=gaset)
	
	