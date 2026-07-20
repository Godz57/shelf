"""Unit tests for legacy ModelAdmin helpers (UI is /manage/, not /admin/)."""

from django.test import TestCase

from catalog.admin import BookAdmin
from catalog.admin_site import shelter_admin_site
from catalog.models import Author, Book, Category, ReadingListItem


class AdminRegistrationTests(TestCase):
    def test_models_still_registered_on_site_object(self):
        for model in (Author, Category, Book, ReadingListItem):
            self.assertTrue(shelter_admin_site.is_registered(model))

    def test_admin_site_branding(self):
        self.assertEqual(shelter_admin_site.site_header, "Your Shelter")
        self.assertFalse(shelter_admin_site.enable_nav_sidebar)


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
        self.book_admin = BookAdmin(Book, shelter_admin_site)

    def test_cover_thumb_uses_img(self):
        html = self.book_admin.cover_thumb(self.book)
        self.assertIn("<img", html)
        self.assertIn(self.book.cover_url, html)

    def test_cover_thumb_fallback_without_url(self):
        self.book.cover_url = ""
        html = self.book_admin.cover_thumb(self.book)
        self.assertIn("shelter-cover-fallback", html)
        self.assertIn("G", html)

    def test_slug_hidden_from_fields(self):
        self.assertIn("slug", self.book_admin.exclude)
