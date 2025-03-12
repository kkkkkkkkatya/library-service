from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from books.models import Book

class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(expected_return_date__gt=models.F("borrow_date")),
                name="check_expected_return_after_borrow",
            ),
            models.CheckConstraint(
                check=models.Q(actual_return_date__gte=models.F("borrow_date")),
                name="check_actual_return_after_borrow",
            ),
        ]

    @staticmethod
    def validate_borrowing(book, error_to_raise):
        """Ensures book inventory is not 0 before borrowing."""
        if book.inventory <= 0:
            raise error_to_raise(
                {"book": f"Book '{book.title}' is out of stock and cannot be borrowed."}
            )

    def clean(self):
        """Runs validation before saving."""
        Borrowing.validate_borrowing(self.book, ValidationError)

    def save(self, *args, **kwargs):
        """Validates, decreases inventory, and saves the borrowing."""
        self.full_clean()
        self.book.inventory -= 1
        self.book.save(update_fields=["inventory"])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} borrowed {self.book} on {self.borrow_date}"
