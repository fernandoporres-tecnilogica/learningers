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
        ranges = make_range_serializer(range_type)(many=True)
        resource = serializers.PrimaryKeyRelatedField(read_only=False,queryset=models.Resource.objects.all())
        links = serializers.PrimaryKeyRelatedField(required=False,many=True,queryset=models.Resource.objects.all())
	def create(self,validated_data):
		ranges = validated_data.pop('ranges')
		ret = models.available_annotation_contents[content_type].objects.create(**validated_data)
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
    
