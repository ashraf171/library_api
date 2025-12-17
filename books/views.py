from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.generic import TemplateView
from .models import Author, Book, BorrowingRecord, UserProfile
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    BorrowingRecordSerializer,
    UserProfileSerializer,
    RegisterSerializer
)
from .permissions import IsOwner
from django.contrib.auth.models import User

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "User registered successfully"}, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profile not found"}, status=404)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class BorrowingRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowingRecord.objects.all()
    serializer_class = BorrowingRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'list', 'my_borrows']:
            return [IsAuthenticated()]
        elif self.action == 'return_book':
            return [IsOwner()]
        return super().get_permissions()

    def get_queryset(self):
        user_profile = self.request.user.profile
        if self.action == 'my_borrows':
            return BorrowingRecord.objects.filter(user=user_profile)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    @action(detail=False, methods=['get'], url_path='my-borrows')
    def my_borrows(self, request):
        queryset = BorrowingRecord.objects.filter(user=request.user.profile)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='return-book')
    def return_book(self, request, pk=None):
        borrow_record = self.get_object()
        borrow_record.return_book()
        serializer = self.get_serializer(borrow_record)
        return Response(serializer.data)


class HomePageView(TemplateView):
    template_name = "books/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.all()
        return context