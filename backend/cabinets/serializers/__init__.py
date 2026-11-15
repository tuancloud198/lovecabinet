from rest_framework import serializers
from ..models import Cabinet
class CabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        fields = ['id', 'couple', 'name', 'year']
        read_only_fields = ['couple']
