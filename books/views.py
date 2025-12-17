

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from django.shortcuts import get_object_or_404

from .models import BorrowingRecord , UserProfile , Book
from .serializers import BorrowingRecordSerializer, RegisterSerializer, UserProfileSerializer, BookSerializer
from .permissions import IsOwner
#1 User Management Views
class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )

class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self):
        return self.request.user.profile



#2 Book Management View

class BookListCreateView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]



class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]













#3 Borrowing Operations
class BorrowingBookView(CreateAPIView):
    queryset = BorrowingRecord.objects.all()
    serializer_class = BorrowingRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)



class BorrowingBookListAPIView(ListAPIView):
    serializer_class = BorrowingRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return BorrowingRecord.objects.filter(
            user=self.request.user.profile
        )



class ReturnBookView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def post(self, request, id, *args, **kwargs):
        borrowing = get_object_or_404(BorrowingRecord, id=id)


        self.check_object_permissions(request, borrowing)

        try:
            borrowing.return_book()
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Book returned successfully."},
            status=status.HTTP_200_OK
        )



