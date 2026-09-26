from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to any user,
    but write (create, update, delete) operations are restricted to staff/admin users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsReviewAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a review (or staff/admin) to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(obj.user == request.user or (request.user and request.user.is_staff))
