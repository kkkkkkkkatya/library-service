from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer


BORROWINGS_URL = reverse("borrowings:borrowing-list")

def sample_book(title="Sample Book", inventory=5):
    """Helper function to create a book."""
    return Book.objects.create(title=title, inventory=inventory)


def sample_borrowing(user, book=None, days=7, actual_return_date=None):
    """Helper function to create a borrowing instance for a given user."""
    if book is None:
        book = sample_book()

    return Borrowing.objects.create(
        user=user,
        book=book,
        borrow_date=date.today(),
        expected_return_date=date.today() + timedelta(days=days),
        actual_return_date=actual_return_date,
    )


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test unauth user can not see borrowings."""
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
        """Test auth user can create borrowing."""
        book = sample_book()

        payload = {
            "book": book.id,
            "expected_return_date": (date.today() + timedelta(days=7)).isoformat(),
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)
        borrowing = Borrowing.objects.first()
        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_with_wrong_expected_return_date(self):
        """Test can not create borrowing with wrong expected return date."""
        book = sample_book()

        payload = {
            "book": book.id,
            "expected_return_date": (date.today() - timedelta(days=1)).isoformat(),
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Borrowing.objects.count(), 0)

    def test_create_borrowing_with_null_inventory(self):
        """Test can not create borrowing using null inventory."""
        book = sample_book(inventory=0)

        payload = {
            "book": book.id,
            "expected_return_date": (date.today() + timedelta(days=7)).isoformat(),
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Borrowing.objects.count(), 0)

    def test_list_borrowings(self):
        """Test get list of borrowings."""
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)

        # Create borrowing for another user
        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="testpass",
        )
        sample_borrowing(user=other_user)


        res = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingReadSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(borrowings))
        self.assertEqual(res.data, serializer.data)

    def test_list_borrowings_filtered_by_active(self):
        """Test filtering borrowings by is_active."""
        active_borrowing1 = sample_borrowing(user=self.user)
        active_borrowing2 = sample_borrowing(user=self.user)

        # Create one inactive borrowing (actual_return_date is set)
        inactive_borrowing = sample_borrowing(
            user=self.user,
            actual_return_date=date.today(),
        )

        res = self.client.get(BORROWINGS_URL, {"is_active": "true"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        serializer1 = BorrowingReadSerializer(active_borrowing1)
        serializer2 = BorrowingReadSerializer(active_borrowing2)
        serializer3 = BorrowingReadSerializer(inactive_borrowing)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_borrowing(self):
        """Test retrieving a single borrowing by ID."""
        borrowing = sample_borrowing(user=self.user)

        url = reverse("borrowings:borrowing-detail", args=[borrowing.id])
        res = self.client.get(url)

        serializer = BorrowingReadSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_return_borrowing(self):
        """Test returning a borrowed book."""
        borrowing = sample_borrowing(user=self.user)

        url = reverse("borrowings:borrowing-return-borrowing", args=[borrowing.id])
        res = self.client.post(url)

        borrowing.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(borrowing.actual_return_date)

    def test_cannot_return_borrowing_twice(self):
        """Test that a book cannot be returned twice."""
        borrowing = sample_borrowing(user=self.user, actual_return_date=date.today())

        url = reverse("borrowings:borrowing-return-borrowing", args=[borrowing.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res.data["detail"], "This borrowing has already been returned."
        )


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_all_borrowings(self):
        """Test that admin can see all borrowings."""
        sample_borrowing(user=self.user)

        other_user1 = get_user_model().objects.create_user(
            email="other1@test.com",
            password="testpass1",
        )
        sample_borrowing(user=other_user1)

        other_user2 = get_user_model().objects.create_user(
            email="other2@test.com",
            password="testpass2",
        )
        sample_borrowing(user=other_user2)


        res = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingReadSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(borrowings))
        self.assertEqual(res.data, serializer.data)

    def test_list_borrowings_filtered_by_user(self):
        """Test that admin can filter borrowings by user ID."""
        user1 = get_user_model().objects.create_user(
            email="user1@test.com",
            password="testpass1",
        )
        user2 = get_user_model().objects.create_user(
            email="user2@test.com",
            password="testpass2",
        )

        borrowing_user1 = sample_borrowing(user=user1)
        borrowing_user2 = sample_borrowing(user=user2)

        res = self.client.get(BORROWINGS_URL, {"user_id": user1.id})

        serializer1 = BorrowingReadSerializer(borrowing_user1)
        serializer3 = BorrowingReadSerializer(borrowing_user2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
