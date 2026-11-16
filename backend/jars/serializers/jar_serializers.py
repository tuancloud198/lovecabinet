from rest_framework import serializers
from jars.models import Jar
class JarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jar
        fields = ['id', 'cabinet', 'name', 'emoji', 'color']
