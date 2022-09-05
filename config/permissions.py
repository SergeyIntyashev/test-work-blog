from rest_framework.permissions import BasePermission, SAFE_METHODS

from blogs.models import Posts


class IsAuthenticatedAndOwner(BasePermission):
    """
    Разрешает доступ аутентифицированному пользователю и владельцу
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated
                    and (obj.owner == request.user))


class IsAuthenticatedAndAuthor(BasePermission):
    """
    Разрешает доступ аутентифицированному пользователю и автору
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated
                    and (request.user in obj.authors.all()))


class IsAdminUser(BasePermission):
    """
    Разрешает доступ администратору
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_admin)


class IsAuthorOrBlogOwner(BasePermission):
    """
    Разрешает доступ автору или владельцу блога
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Posts):
            obj = obj.blog

        return bool((request.user in obj.authors.all())
                    or (obj.owner == request.user))


class IsAdminOrReadOnly(BasePermission):
    """
    Доступ на чтение или для администратора
    """

    def has_permission(self, request, view):
        return bool((request.method in SAFE_METHODS) or
                    (request.user and request.user.is_admin))
