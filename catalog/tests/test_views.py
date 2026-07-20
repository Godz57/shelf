from django.test import TestCase
from django.urls import reverse

from catalog.models import Author, Book, Category


class CatalogViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Theology", slug="theology")
        self.author = Author.objects.create(name="Jane Doe", slug="jane-doe", bio="Bio")
        self.book = Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="A careful look at grace.",
            category=self.category,
            is_featured=True,
        )
        self.book.authors.add(self.author)

    def test_home_200_and_shows_featured(self):
        res = self.client.get(reverse("catalog:home"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Grace and Truth")

    def test_book_list_200(self):
        res = self.client.get(reverse("catalog:book_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Grace and Truth")

    def test_book_detail_200(self):
        res = self.client.get(self.book.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Grace and Truth")
        self.assertContains(res, "Jane Doe")

    def test_author_detail_200(self):
        res = self.client.get(self.author.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Jane Doe")
        self.assertContains(res, "Grace and Truth")

    def test_search_by_title(self):
        res = self.client.get(reverse("catalog:book_list"), {"q": "Grace"})
        self.assertContains(res, "Grace and Truth")
        res = self.client.get(reverse("catalog:book_list"), {"q": "xyznope"})
        self.assertNotContains(res, "Grace and Truth")

    def test_filter_by_category(self):
        other = Category.objects.create(name="Biography", slug="biography")
        Book.objects.create(
            title="Other Book",
            slug="other-book",
            description="d",
            category=other,
        )
        res = self.client.get(
            reverse("catalog:book_list"), {"category": "theology"}
        )
        self.assertContains(res, "Grace and Truth")
        self.assertNotContains(res, "Other Book")

    def test_sort_title(self):
        Book.objects.create(
            title="Alpha",
            slug="alpha",
            description="d",
            category=self.category,
        )
        res = self.client.get(reverse("catalog:book_list"), {"sort": "title"})
        self.assertEqual(res.status_code, 200)
        content = res.content.decode()
        self.assertLess(content.index("Alpha"), content.index("Grace and Truth"))
