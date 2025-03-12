from rest_framework import viewsets, permissions
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.select_related("book", "user")

        # Filter by active borrowings (not returned yet)
        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            is_active = is_active.lower() == "true"
            if is_active:
                queryset = queryset.filter(actual_return_date__isnull=True)
            else:
                queryset = queryset.filter(actual_return_date__isnull=False)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action in ["list", "retrieve"]:
            return BorrowingReadSerializer
        return BorrowingCreateSerializer
