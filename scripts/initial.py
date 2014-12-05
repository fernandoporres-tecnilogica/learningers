# -*- coding: utf-8 -*-
from catalog import models
from django.contrib.auth.models import User
from django.utils.translation import activate
from datetime import datetime
from schedule.models import Rule, Event
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, HOURLY, MINUTELY, SECONDLY

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

	# install a geolocation
	berlin,created = models.GeoLocation.objects.get_or_create(address='Berlin')
	nicol,created = models.GeoLocation.objects.get_or_create(address='90 chemin de Nicol, 31200 Toulouse, France')
	
	# create parcours
	enscene,created = models.Way.objects.get_or_create(name=u'En Scène', description=u'Atelier de théâtre', slug='En_Scene')
	impro,created = models.Way.objects.get_or_create(name=u'I.M.P.R.O.', description=u'Atelier d\'improvisation théâtrale', slug='I.M.P.R.O')
	revo,created = models.Way.objects.get_or_create(name=u'La révolution Russe',description=u'Documentation sur la révolution russe',slug='revolution-russe')
	
	# create some events
	weekly,created = Rule.objects.get_or_create(name='Hebdo',description=u'Répétition hebdomadaire',frequency=WEEKLY)
	evt,created = Event.objects.get_or_create(title=u'En Scène 2012-2013, Ubu Roi',start=datetime(2012, 10, 11, 20, 00, 00),end=datetime(2012, 10, 11, 22, 00, 00),rule=weekly)
	x1,created = models.Initiative.objects.get_or_create(parent=enscene,description=u'Atelier en Scène 2012-2013. Mise en scène de la pièce UBU ROI d\'Alfred Jarry',event=evt)

