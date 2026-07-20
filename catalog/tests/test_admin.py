from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from catalog.admin import BookAdmin
from catalog.models import Author, Book, Category, ReadingListItem


class AdminRegistrationTests(TestCase):
    def test_models_registered(self):
        for model in (Author, Category, Book, ReadingListItem):
            self.assertTrue(admin.site.is_registered(model))

    def test_admin_branding(self):
        self.assertEqual(admin.site.site_header, "Your Shelter Admin")
        self.assertEqual(admin.site.site_title, "Your Shelter")


class BookAdminDisplayTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Theology", slug="theology")
        self.book = Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="Sample description for tests.",
            category=self.category,
            cover_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=200",
        )
        self.book_admin = BookAdmin(Book, admin.site)

    def test_cover_thumb_uses_img(self):
        html = self.book_admin.cover_thumb(self.book)
        self.assertIn("<img", html)
        self.assertIn(self.book.cover_url, html)

    def test_cover_thumb_fallback_without_url(self):
        self.book.cover_url = ""
        html = self.book_admin.cover_thumb(self.book)
        self.assertIn("shelter-cover-fallback", html)
        self.assertIn("G", html)


class AdminSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="complex-pass-123",
        )
        self.client = Client()
        self.client.login(username="admin", password="complex-pass-123")
        cat = Category.objects.create(name="Theology", slug="theology")
        Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="d",
            category=cat,
        )

    def test_admin_index_loads(self):
        res = self.client.get(reverse("admin:index"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Your Shelter")

    def test_book_changelist_loads(self):
        res = self.client.get(reverse("admin:catalog_book_changelist"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Grace and Truth")

    def test_reading_list_verbose_name(self):
        res = self.client.get(reverse("admin:index"))
        self.assertContains(res, "Your Shelter items")
