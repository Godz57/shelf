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
        Book.objects.create(
            title="Morning Light",
            slug="morning-light",
            description="A short devotion.",
            category=cat,
        )

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
        self.assertEqual(data["category_slug"], "theology")

    def test_list_search_q(self):
        res = self.client.get("/api/books/", {"q": "Grace"})
        self.assertEqual(res.status_code, 200)
        titles = [b["title"] for b in res.json()["results"]]
        self.assertIn("Grace and Truth", titles)
        self.assertNotIn("Morning Light", titles)

    def test_easter_query_includes_hidden_book(self):
        res = self.client.get("/api/books/", {"easter": "true"})
        self.assertEqual(res.status_code, 200)
        results = res.json()["results"]
        hidden = [b for b in results if b.get("hidden") is True]
        self.assertEqual(len(hidden), 1)
        self.assertEqual(hidden[0]["slug"], "the-quiet-room")
        self.assertIn("curious", hidden[0]["description"].lower())

    def test_list_without_easter_has_no_hidden(self):
        res = self.client.get("/api/books/")
        results = res.json()["results"]
        self.assertFalse(any(b.get("hidden") for b in results))

    def test_pick_returns_a_book(self):
        res = self.client.get("/api/books/pick/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn(data["slug"], {"grace-and-truth", "morning-light"})
        self.assertIn("title", data)
