# -*- coding: utf-8 -*-
import catalog.models.base
import catalog.models.meeting
import catalog.models.human
import catalog.models.mailman
from catalog.models.way import SessionWay
from catalog.models.wiki import Wiki
from catalog.models.base import available_resource_models, GeoLocation, ResourceLanguage, Resource
import reversion
import sys

for model in available_resource_models.values():
    reversion.register(model, follow=['resource_ptr'])
    setattr(sys.modules[__name__],model.__name__, model)