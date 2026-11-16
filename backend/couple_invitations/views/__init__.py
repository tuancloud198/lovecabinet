from rest_framework.decorators import api_view
from rest_framework.response import Response
from couple_invitations.services import create_invitation, accept_invitation, decline_invitation, list_invitations
from couple_invitations.serializers.invitation_serializers import InviteByTagSerializer, InvitationSerializer
@api_view(['GET', 'POST'])
def invitations(request):
    if request.method == 'GET':
        received, sent = list_invitations(request.user)
        return Response({'received': InvitationSerializer(received, many=True).data, 'sent': InvitationSerializer(sent, many=True).data})
    serializer = InviteByTagSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    invitation = create_invitation(request.user, serializer.validated_data['tag'])
    return Response(InvitationSerializer(invitation).data, status=201)
@api_view(['POST'])
def accept(request, pk):
    couple = accept_invitation(request.user, pk)
    return Response({'couple_id': couple.pk})
@api_view(['POST'])
def decline(request, pk):
    decline_invitation(request.user, pk)
    return Response(status=204)
