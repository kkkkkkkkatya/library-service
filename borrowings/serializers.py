from django.core.exceptions import ValidationError
from rest_framework import serializers
from borrowings.models import Borrowing
from books.serializers import BookSerializer


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = ["id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user"]
        read_only_fields = ["id", "borrow_date", "user"]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating borrowings with inventory validation."""

    class Meta:
        model = Borrowing
        fields = ["id", "expected_return_date", "book"]

    def validate(self, attrs):
        """Validate borrowing using the model method before saving."""
        data = super().validate(attrs)
        Borrowing.validate_borrowing(attrs["book"], ValidationError)
        return data

    def create(self, validated_data):
        """Attach the current user and create a borrowing after validation."""
        user = self.context["request"].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)
        return borrowing