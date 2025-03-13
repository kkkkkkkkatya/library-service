from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id):
    """Return book detail URL"""
    return reverse("books:book-detail", args=[book_id])


def sample_book(**params):
    """Create and return a sample book"""
    defaults = {
        "title": "Sample Book",
        "author": "John Doe",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": Decimal("5.00"),
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    """Test book API access for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        """Test that anyone can list books"""
        sample_book()
        sample_book(title="Another Book")

        res = self.client.get(BOOKS_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        """Test that anyone can retrieve book details"""
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden_unauthorized(self):
        """Test that non-admin users cannot create a book"""
        payload = {
            "title": "Unauthorized Book",
            "author": "Jane Doe",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": Decimal("3.00"),
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    """Test book API access for authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden_authorized(self):
        """Test that non-admin users cannot create a book"""
        payload = {
            "title": "Unauthorized Book",
            "author": "Jane Doe",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": Decimal("3.00"),
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    """Test book API access for admin users"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@admin.com", "password123"
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_book(self):
        """Test that an admin user can create a book"""
        payload = {
            "title": "New Book",
            "author": "Admin Author",
            "cover": "HARD",
            "inventory": 7,
            "daily_fee": Decimal("4.50"),
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_update_book(self):
        """Test that an admin user can update a book"""
        book = sample_book()

        payload = {"title": "Updated Title"}
        url = detail_url(book.id)
        res = self.client.patch(url, payload)

        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.title, payload["title"])

    def test_delete_book(self):
        """Test that an admin user can delete a book"""
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
