# -*- coding: utf-8 -*-
"""
Les serializers utiles à l'interface REST framework du catalogue,
utilisée pour la communication AJAX
"""
from rest_framework import serializers
import models

class ResourceSerializer(serializers.ModelSerializer):
    """
    Serializer attaché à une ressource générique.
    
    Utilisé pour la suppression de ressources. 
    """
    name = serializers.SerializerMethodField('getname')
    content = serializers.SerializerMethodField('getcontent')
    class Meta:
        model = models.Resource
        fields = ('name','content',)
    def getname(self,obj):
        return "<a href='" + obj.get_absolute_url() + "'>" + obj.name + "</a>"
    def getcontent(self,obj):
        return "<p>" + obj.description + "</p>"
    