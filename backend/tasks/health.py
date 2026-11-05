from django.db import connection
from django.http import JsonResponse


def health(request):
    """Smoke-test endpoint for deploy: 200 when the app and DB respond."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db = "ok"
    except Exception:
        return JsonResponse({"status": "error", "db": "unreachable"}, status=503)
    return JsonResponse({"status": "ok", "db": db})
