# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

# User profile class
class UserProfile(models.Model):
    """ 
    Profil d'un.e utilisat.eur.rice enregistr.é.e
    """
    user = models.OneToOneField(User, related_name='profile', primary_key=True)
