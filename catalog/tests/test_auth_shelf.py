from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Book, Category, ReadingListItem


class AuthTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        res = self.client.post(
            reverse("catalog:signup"),
            {
                "username": "newreader",
                "password1": "complex-pass-123",
                "password2": "complex-pass-123",
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(
            get_user_model().objects.filter(username="newreader").exists()
        )

    def test_login_logout(self):
        User = get_user_model()
        User.objects.create_user(username="reader", password="complex-pass-123")
        res = self.client.post(
            reverse("login"),
            {"username": "reader", "password": "complex-pass-123"},
        )
        self.assertEqual(res.status_code, 302)
        res = self.client.post(reverse("logout"))
        self.assertEqual(res.status_code, 302)


class ReadingListTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="reader", password="complex-pass-123"
        )
        cat = Category.objects.create(name="Theology", slug="theology")
        self.book = Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="d",
            category=cat,
        )

    def test_add_requires_login(self):
        res = self.client.post(
            reverse("catalog:shelf_add", kwargs={"book_id": self.book.pk})
        )
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse("login"), res.url)

    def test_add_and_list_and_remove(self):
        self.client.login(username="reader", password="complex-pass-123")
        res = self.client.post(
            reverse("catalog:shelf_add", kwargs={"book_id": self.book.pk})
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(
            ReadingListItem.objects.filter(user=self.user, book=self.book).exists()
        )
        res = self.client.get(reverse("catalog:my_shelf"))
        self.assertContains(res, "Grace and Truth")
        res = self.client.post(
            reverse("catalog:shelf_remove", kwargs={"book_id": self.book.pk})
        )
        self.assertEqual(res.status_code, 302)
        self.assertFalse(
            ReadingListItem.objects.filter(user=self.user, book=self.book).exists()
        )
