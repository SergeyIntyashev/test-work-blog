from rest_framework.permissions import BasePermission


class IsAuthenticatedAndOwner(BasePermission):
    """
    Разрешает доступ аутентифицированному пользователю и владельцу
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated
                    and (obj.user == request.user))


class IsAuthenticatedAndAuthor(BasePermission):
    """
    Разрешает доступ аутентифицированному пользователю и автору
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated
                    and (request.user in obj.authors))


class IsAdminUser(BasePermission):
    """
    Разрешает доступ администратору
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_admin)
