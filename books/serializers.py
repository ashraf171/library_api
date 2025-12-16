from rest_framework import serializers
from .models import Author,Book,BorrowingRecord, UserProfile


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Author
        fields=['id','name','bio','birth_year']
        read_only_fields=['id']


class BookSerializer(serializers.ModelSerializer):
    author=serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    author_name = serializers.ReadOnlyField(source='author.name')
    class Meta:
        model=Book
        fields=['id','title','author','author_name','isbn','publication_year','genre','total_copies','available_copies','cover_image']
        read_only_fields=['id','available_copies']
    
    
    def validate_isbn(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("ISBN must contain only numbers.")
        return value
    

class BorrowingRecordSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    user_name = serializers.ReadOnlyField(source='user.user.username')
    book=serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    book_title = serializers.ReadOnlyField(source='book.title')
    class Meta:
        model=BorrowingRecord
        fields=[
            'id','user', 'user_name',
            'book','book_title',
            'borrow_date','due_date',
            'return_date','is_returned'
        ]
        read_only_fields = [
            'id', 'borrow_date', 'due_date',
            'return_date', 'is_returned'
        ]

