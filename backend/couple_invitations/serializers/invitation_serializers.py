from rest_framework import serializers
from users.models import TAG_LENGTH
from couple_invitations.models import Invitation
class InviteByTagSerializer(serializers.Serializer):
    tag = serializers.CharField(max_length=TAG_LENGTH + 1)
class InvitationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    def person(self, user):
        return {'id': user.pk, 'display_name': user.display_name, 'tag': user.tag}
    def get_sender(self, obj):
        return self.person(obj.sender)
    def get_recipient(self, obj):
        return self.person(obj.recipient)
    class Meta:
        model = Invitation
        fields = ['id', 'sender', 'recipient', 'created_at', 'expires_at']
