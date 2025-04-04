# Generated by Django 5.1.7 on 2025-03-08 17:29

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                (
                    "cover",
                    models.CharField(
                        choices=[("HARD", "Hardcover"), ("SOFT", "Softcover")],
                        max_length=10,
                    ),
                ),
                ("inventory", models.PositiveIntegerField()),
                (
                    "daily_fee",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=6
                    ),
                ),
            ],
        ),
    ]
