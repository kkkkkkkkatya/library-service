from django.db import models
from decimal import Decimal


class Book(models.Model):
    COVER_CHOICES = [
        ("HARD", "Hardcover"),
        ("SOFT", "Softcover"),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=10, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"{self.title} by {self.author}"
