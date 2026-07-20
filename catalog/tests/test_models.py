from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from catalog.models import Author, Book, Category, ReadingListItem


class AuthorModelTests(TestCase):
    def test_str_and_absolute_url(self):
        author = Author.objects.create(name="Jane Doe", slug="jane-doe")
        self.assertEqual(str(author), "Jane Doe")
        self.assertEqual(
            author.get_absolute_url(),
            reverse("catalog:author_detail", kwargs={"slug": "jane-doe"}),
        )


class BookModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Theology", slug="theology")
        self.author = Author.objects.create(name="Jane Doe", slug="jane-doe")
        self.book = Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            subtitle="A short study",
            description="Sample description for tests.",
            category=self.category,
            is_featured=True,
        )
        self.book.authors.add(self.author)

    def test_str(self):
        self.assertEqual(str(self.book), "Grace and Truth")

    def test_absolute_url(self):
        self.assertEqual(
            self.book.get_absolute_url(),
            reverse("catalog:book_detail", kwargs={"slug": "grace-and-truth"}),
        )

    def test_authors_m2m(self):
        self.assertEqual(self.book.authors.count(), 1)


class ReadingListItemTests(TestCase):
    def test_unique_user_book(self):
        User = get_user_model()
        user = User.objects.create_user(username="reader", password="pass12345")
        category = Category.objects.create(name="Devotional", slug="devotional")
        book = Book.objects.create(
            title="Morning Light",
            slug="morning-light",
            description="x",
            category=category,
        )
        ReadingListItem.objects.create(user=user, book=book)
        with self.assertRaises(IntegrityError):
            ReadingListItem.objects.create(user=user, book=book)
