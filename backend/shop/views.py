from rest_framework.decorators import api_view
from rest_framework.response import Response
from common.services import couple_for
from shop.services import buy, catalog, wallet


def _state(couple):
    return {**wallet(couple), 'items': catalog(couple)}


@api_view(['GET'])
def shop(request):
    """The couple's shop points (earned / spent / balance) and the items, with what's owned."""
    return Response(_state(couple_for(request.user)))


@api_view(['POST'])
def buy_item(request, item):
    couple = couple_for(request.user)
    buy(couple, request.user, item)
    return Response(_state(couple), status=201)
