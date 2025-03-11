from django.urls import path, include
from rest_framework.routers import DefaultRouter
from borrowings.views import BorrowingViewSet

router = DefaultRouter()
router.register("", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowings"
