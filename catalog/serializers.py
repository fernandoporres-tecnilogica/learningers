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
    name = serializers.SerializerMethodField('get_name')
    content = serializers.SerializerMethodField('get_content')
    class Meta:
        model = models.Resource
        fields = ('name','content',)
    def get_name(self,obj):
        return "<a href='" + obj.get_absolute_url() + "'>" + obj.name + "</a>"
    def get_content(self,obj):
        return "<p>" + obj.name + "</p><p>" + obj.description + "</p>"
    
def make_content_serializer(content_type):
    class HOP(serializers.ModelSerializer):
        class Meta:
            model = models.available_annotation_contents[content_type]
    return HOP

def make_range_serializer(range_type):
    class HOP(serializers.ModelSerializer):
        class Meta:
            model = models.available_annotation_ranges[range_type]
            read_only_fields = ('annotation',)
    return HOP
                        
def make_annotation_serializer(content_type,range_type):
    class HOP(serializers.ModelSerializer):
        #content = make_content_serializer(content_type)()
        ranges = make_range_serializer(range_type)(many=True)
        resource = serializers.PrimaryKeyRelatedField(source='resource',read_only=False)
        links = serializers.PrimaryKeyRelatedField(source='links',required=False,many=True)
        class Meta:
            model = models.available_annotation_contents[content_type]
            depth = 1
    return HOP
    