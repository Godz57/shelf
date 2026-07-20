from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from catalog.admin import BookAdmin
from catalog.admin_site import shelter_admin_site
from catalog.models import Author, Book, Category, ReadingListItem


class AdminRegistrationTests(TestCase):
    def test_models_registered(self):
        for model in (Author, Category, Book, ReadingListItem):
            self.assertTrue(shelter_admin_site.is_registered(model))

    def test_admin_branding(self):
        self.assertEqual(shelter_admin_site.site_header, "Your Shelter Admin")
        self.assertEqual(shelter_admin_site.site_title, "Your Shelter")


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

    def test_featured_action_updates_queryset(self):
        self.book.is_featured = False
        self.book.save(update_fields=["is_featured"])
        qs = Book.objects.filter(pk=self.book.pk)
        updated = qs.update(is_featured=True)
        self.assertEqual(updated, 1)
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_featured)
        self.assertTrue(hasattr(self.book_admin, "make_featured"))


class AdminSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin",
        )
        self.client = Client()
        self.client.login(username="admin", password="admin")
        cat = Category.objects.create(name="Theology", slug="theology")
        Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="d",
            category=cat,
        )

    def test_admin_index_loads_with_dashboard(self):
        res = self.client.get(reverse("admin:index"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Your Shelter")
        self.assertContains(res, "Quick actions")
        self.assertContains(res, "Add a book")
        self.assertContains(res, "Friendly tips")

    def test_book_changelist_loads(self):
        res = self.client.get(reverse("admin:catalog_book_changelist"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Grace and Truth")

    def test_saved_books_label(self):
        res = self.client.get(reverse("admin:index"))
        self.assertContains(res, "Saved books")

    def test_login_page_hint(self):
        self.client.logout()
        res = self.client.get(reverse("admin:login"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Staff sign-in")
