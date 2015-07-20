# -*- coding: utf-8 -*-
"""
Les serializers utiles à l'interface REST framework du catalogue,
utilisée pour la communication AJAX
"""
from rest_framework import serializers
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import models

class ResourceSerializer(serializers.ModelSerializer):
    """
    Serializer attaché à une ressource générique.
    
    Utilisé pour la suppression de ressources. 
    """
    name = serializers.SerializerMethodField()
    rendered = serializers.SerializerMethodField()
    class Meta:
        model = models.Resource
        fields = ('name','rendered',)
    def get_name(self,obj):
        return "<a href='" + obj.get_absolute_url() + "'>" + obj.name + "</a>"
    def get_rendered(self,obj):
        args = { 'resource_type': obj.resource_type, 
             'resource_source': 'internal',
             'resource_name': obj.name,
             'resource_description' : obj.preview(),
             'resource_tooltip' : obj.description,
             'resource_url': obj.get_absolute_url(),
        }
        return render_to_string('catalog/resource.html',args)
    
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
        ranges = make_range_serializer(range_type)(many=True,required=True)
        resource = serializers.PrimaryKeyRelatedField(required=True,read_only=False,queryset=models.Resource.objects.all())
        links = serializers.PrimaryKeyRelatedField(required=False,many=True,queryset=models.Resource.objects.all())
        authors = serializers.PrimaryKeyRelatedField(required=False,many=True,queryset=User.objects.all())
        rendered = serializers.SerializerMethodField()
        def get_rendered(self,obj):
            return render_to_string('catalog/annotation.html',{'annotation':obj})        
        def create(self,validated_data):
            ranges = validated_data.pop('ranges')
            m2m_data = {}
            # we need to take care separately of manytomany fields.
            for name,field in self.fields.items():
                if isinstance(field,serializers.ManyRelatedField) and name in validated_data:
                    m2m_data[name] = validated_data.pop(name)
            ret = models.available_annotation_contents[content_type].objects.create(**validated_data)
            for k,v in m2m_data.items():
                for elem in v:
                    rel = self.fields[k].child_relation.queryset.model.objects.create(**elem)
                    getattr(ret,k).add(rel)
            for r in ranges:
                r['annotation_id'] = ret.pk
            self.fields['ranges'].create(ranges)
            return ret
        def update(self,instance,validated_data):
            # ignore range because it cannot be changed!
            validated_data.pop('ranges')
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        class Meta:
            model = models.available_annotation_contents[content_type]
            depth = 1
    return HOP
    
class CommentSerializer(serializers.ModelSerializer):
    rendered = serializers.SerializerMethodField()
    def get_rendered(self,obj):
        return render_to_string('catalog/comment.html',{'comment':obj})        
    class Meta:
        model = models.Comment
        
