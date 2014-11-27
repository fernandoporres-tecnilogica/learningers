from django.contrib.auth.models import User
from django.db import models

# User profile class
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', primary_key=True)
