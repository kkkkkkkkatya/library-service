from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer
)


class BorrowingViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
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

        user_id = self.request.query_params.get("user_id", None)
        if self.request.user.is_staff:
            if user_id is not None:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        if self.action in ["list", "retrieve"]:
            return BorrowingReadSerializer
        return BorrowingCreateSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by active borrowings (not returned yet). Use ?is_active=true or ?is_active=false",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by specific user ID (Admins only). Use ?user_id=1",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @action(detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated])
    def return_borrowing(self, request, pk=None):
        """Mark a borrowing as returned and increase book inventory."""
        borrowing = self.get_object()

        # Only borrower or admin can return the book
        if request.user != borrowing.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to return this book."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if already returned
        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update return date and inventory
        borrowing.actual_return_date = date.today()
        borrowing.book.inventory += 1
        borrowing.book.save(update_fields=["inventory"])
        borrowing.save(update_fields=["actual_return_date"])

        return Response({"message": "Book returned successfully!"}, status=status.HTTP_200_OK)
