"""Probe endpoints for Kubernetes. Plain Django views, so DRF's auth and rate limits don't apply."""
from django.db import connection
from django.http import JsonResponse

def live(request):
    return JsonResponse({'status': 'ok'})

def ready(request):
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({'status': 'database unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})
