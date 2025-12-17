from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    ProfileView,
    BookViewSet,
    BorrowingRecordViewSet,
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrowings', BorrowingRecordViewSet, basename='borrowing')

urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),

]
urlpatterns+=router.urls
