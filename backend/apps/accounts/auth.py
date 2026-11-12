from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

STUDENT_SCOPES = ["tasks:read", "solutions:read", "solutions:write", "solutions:vote"]
TEACHER_SCOPES = ["tasks:read", "tasks:write", "solutions:read", "solutions:vote", "feedback:write"]


def scopes_for(user):
    return TEACHER_SCOPES if user.is_teacher else STUDENT_SCOPES


def request_scopes(request):
    if request.auth is not None:
        return request.auth.get("scopes", [])
    return scopes_for(request.user)


class ScopedTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["scopes"] = scopes_for(user)
        return token


class HasScopes(BasePermission):
    """
    Widoki deklarują scopy per metoda HTTP:
        required_scopes = {"GET": ["tasks:read"], "POST": ["tasks:write"]}
    """

    message = "Missing required scope."

    def has_permission(self, request, view):
        required = getattr(view, "required_scopes", {}).get(request.method, [])
        return set(required) <= set(request_scopes(request))