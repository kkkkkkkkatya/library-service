from datetime import date

from django.core.exceptions import ValidationError
from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer
from utils.telegram_helper import send_telegram_message


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
        data = super().validate(attrs)

        borrowing = Borrowing(
            book=attrs["book"],
            expected_return_date=attrs["expected_return_date"],
            user=self.context["request"].user,
            borrow_date=date.today(),
        )

        try:
            borrowing.validate()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return data

    def create(self, validated_data):
        """Attach the current user and create a borrowing."""
        user = self.context["request"].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)

        message = (
            f"New Borrowing Created:\n"
            f"User: {user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Expected Return Date: {borrowing.expected_return_date}"
        )
        send_telegram_message(message)

        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    """Serializer for returning a borrowed book."""

    class Meta:
        model = Borrowing
        fields = ["id", "actual_return_date"]
        read_only_fields = ["id", "actual_return_date"]

    def update(self, instance, validated_data):
        """Handles book return logic."""
        if instance.actual_return_date is not None:
            raise serializers.ValidationError({"actual_return_date": "This borrowing has already been returned."})

        instance.return_borrowing()
        return instance
