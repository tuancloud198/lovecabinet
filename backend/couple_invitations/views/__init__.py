from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services import create_invitation, accept_invitation
from ..serializers import InvitationCodeSerializer
@api_view(['POST'])
def create(request):
    invitation = create_invitation(request.user)
    return Response({'code': invitation.code, 'expires_at': invitation.expires_at}, status=201)
@api_view(['POST'])
def accept(request):
    serializer = InvitationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    couple = accept_invitation(request.user, serializer.validated_data['code'])
    return Response({'couple_id': couple.pk})
