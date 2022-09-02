from rest_framework.permissions import BasePermission


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
    Разрешает доступ автору или владельцу блога, которому принадлежит пост
    """

    def has_object_permission(self, request, view, obj):
        return bool((request.user in obj.blog.authors.all())
                    or (obj.blog.owner == request.user))
