from rest_framework import serializers
class InvitationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
