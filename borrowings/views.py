from rest_framework import viewsets, permissions
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.select_related("book", "user")
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action in ["list", "retrieve"]:
            return BorrowingReadSerializer
        return BorrowingCreateSerializer
