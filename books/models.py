from datetime import timedelta, date

from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from books.constants import MEMBERSHIP_CHOICES, GENRE_CHOICES


class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    phone_number = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    membership_type = models.CharField(max_length=10,choices=MEMBERSHIP_CHOICES)
    is_active_member = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Author(models.Model):
    current_year = date.today().year

    name = models.CharField(max_length=120, db_index=True)
    bio = models.TextField(blank=True, null=True)
    birth_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(current_year)
        ]
    )

    def __str__(self):
        return self.name


class Book(models.Model):
    current_year = date.today().year

    title = models.CharField(max_length=120, db_index=True)
    author = models.ForeignKey(Author,on_delete=models.CASCADE,related_name='books')
    isbn = models.CharField(max_length=20, unique=True, db_index=True)
    publication_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(current_year)
        ]
    )
    genre = models.CharField(max_length=20,choices=GENRE_CHOICES)
    total_copies = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    available_copies = models.PositiveIntegerField(editable=False)
    cover_image = models.ImageField(upload_to='book_covers/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        
        if self.pk is None:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)

    def is_available(self):
        return self.available_copies > 0

    def decrease_available(self):
        if self.available_copies <= 0:
            raise ValidationError("No available copies.")
        self.available_copies -= 1
        self.save(update_fields=['available_copies'])

    def increase_available(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save(update_fields=['available_copies'])

    def __str__(self):
        return self.title


class BorrowingRecord(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='borrowings')
    book = models.ForeignKey(Book,on_delete=models.PROTECT,related_name='borrowings')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    def clean(self):
        
        if not self.book.is_available():
            raise ValidationError("This book is not available for borrowing.")

        existing = BorrowingRecord.objects.filter(
            user=self.user,
            book=self.book,
            is_returned=False
        )

        if self.pk:
            existing = existing.exclude(pk=self.pk)

        if existing.exists():
            raise ValidationError(
                "You already borrowed this book and did not return it."
            )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        with transaction.atomic():
            if is_new:
                self.full_clean()
                if not self.due_date:
                    self.due_date = timezone.now() + timedelta(days=14)

            super().save(*args, **kwargs)

            if is_new:
                self.book.decrease_available()

    def return_book(self):
        if self.is_returned:
            raise ValidationError("This borrowing is already returned.")

        with transaction.atomic():
            self.is_returned = True
            self.return_date = timezone.now()
            self.save(update_fields=['is_returned', 'return_date'])
            self.book.increase_available()

    def __str__(self):
        return f"{self.user.user.username} borrowed {self.book.title}"
