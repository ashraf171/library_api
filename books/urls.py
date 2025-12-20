from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    ProfileView,
    BookViewSet,
    BorrowingRecordViewSet,
    HomePageView,
    AuthorViewSet
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrowings', BorrowingRecordViewSet, basename='borrowing')
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),

]
urlpatterns+=router.urls
