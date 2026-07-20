from django.test import TestCase

from catalog.models import Author, Book, Category


class BookAPITests(TestCase):
    def setUp(self):
        cat = Category.objects.create(name="Theology", slug="theology")
        author = Author.objects.create(name="Jane Doe", slug="jane-doe")
        self.book = Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="A careful look at grace.",
            category=cat,
            is_featured=True,
        )
        self.book.authors.add(author)

    def test_list_json(self):
        res = self.client.get("/api/books/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        results = data["results"] if "results" in data else data
        titles = [b["title"] for b in results]
        self.assertIn("Grace and Truth", titles)

    def test_detail_json(self):
        res = self.client.get(f"/api/books/{self.book.slug}/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["title"], "Grace and Truth")
        self.assertEqual(data["slug"], "grace-and-truth")
        self.assertIn("Jane Doe", data["authors"])
