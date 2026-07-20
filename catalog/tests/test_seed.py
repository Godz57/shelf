from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from catalog.models import Book


class SeedCommandTests(TestCase):
    def test_seed_creates_books(self):
        out = StringIO()
        call_command("seed_catalog", stdout=out)
        self.assertGreaterEqual(Book.objects.count(), 16)
        self.assertIn("Seeded", out.getvalue())
        with_covers = Book.objects.exclude(cover_url="").count()
        self.assertGreaterEqual(with_covers, 16)
        sample = Book.objects.exclude(cover_url="").first()
        self.assertTrue(sample.cover_url.startswith("https://"))
