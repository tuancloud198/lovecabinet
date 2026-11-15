from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
def health(request):
    return JsonResponse(
        {
            "status": "ok",
            "status_code": 200
        },
        status = 200
    )

def get_user(request, user_id):
    if user_id == 1:
        return JsonResponse({
            "id":1,
            "name":"tuan"
        }, status = 200)
    
    if user_id == 2:
        return JsonResponse({
            "id":2,
            "name":"phuong"
        }, status = 200)
    
    else:
        return JsonResponse({
            "id":-1,
            "name": "unknown"
        }, status = 400)