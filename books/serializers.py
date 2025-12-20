from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Author, Book, BorrowingRecord, UserProfile
from books.constants import MEMBERSHIP_CHOICES


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=True)
    address = serializers.CharField(required=False, allow_blank=True)
    membership_type = serializers.ChoiceField(choices=MEMBERSHIP_CHOICES)

    def validate_phone_number(self, value):
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value


    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        profile = UserProfile.objects.create(
            user=user,
            phone_number=validated_data['phone_number'],
            address=validated_data.get('address', ''),
            membership_type=validated_data['membership_type']
        )
        return profile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'phone_number', 'address', 'membership_type']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'birth_year']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    author_name = serializers.ReadOnlyField(source='author.name')

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_name',
            'isbn', 'publication_year', 'genre',
            'total_copies', 'available_copies', 'cover_image'
        ]
        read_only_fields = ['id', 'available_copies']

    def validate_isbn(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("ISBN must contain only numbers.")
        return value


class BorrowingRecordSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    user_name = serializers.ReadOnlyField(source='user.user.username')
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    book_title = serializers.ReadOnlyField(source='book.title')

    class Meta:
        model = BorrowingRecord
        fields = [
            'id', 'user', 'user_name',
            'book', 'book_title',
            'borrow_date', 'due_date',
            'return_date', 'is_returned'
        ]
        read_only_fields = [
            'id', 'borrow_date', 'due_date',
            'return_date', 'is_returned'
        ]
