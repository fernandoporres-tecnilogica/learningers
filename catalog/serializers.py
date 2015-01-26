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
            read_only_fields = ('resource',)
    return HOP
                        
def make_annotation_serializer(content_type,range_type):
    class HOP(serializers.ModelSerializer):
        #content = make_content_serializer(content_type)()
        ranges = make_range_serializer(range_type)(read_only=True)
        class Meta:
            model = models.available_annotation_contents[content_type]
        def create(self, validated_data):
#            content_data = validated_data.pop('content')
#            self.content.create(content_data)
            content = super(HOP,self).create(self,validated_data)
            range_data = validated_data.pop('range')
            self.range.create(range_data,resource=content.resource)
            return content
    return HOP
    