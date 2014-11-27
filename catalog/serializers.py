from rest_framework import serializers
import models

class ResourceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('getname')
    content = serializers.SerializerMethodField('getcontent')
    class Meta:
        model = models.Resource
        fields = ('name','content',)
    def getname(self,obj):
        return "<a href='" + obj.get_absolute_url() + "'>" + obj.name + "</a>"
    def getcontent(self,obj):
        return "<p>" + obj.description + "</p>"
    