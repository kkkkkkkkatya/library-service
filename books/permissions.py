from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission:
    - All users (even unauthenticated ones) can view books (GET, HEAD, OPTIONS).
    - Only admin users can create, update, or delete books.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user and request.user.is_staff
