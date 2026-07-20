from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from catalog.models import StaffProfile
from catalog.permissions import get_staff_access

User = get_user_model()


class AccountAndTeamTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="a@example.com",
            password="admin",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="ComplexPass123!",
        )
        self.editor.is_staff = True
        self.editor.save()
        StaffProfile.objects.create(
            user=self.editor,
            can_manage_books=True,
            can_manage_authors=False,
            can_manage_categories=False,
            can_view_saved=False,
            can_manage_team=False,
        )
        self.client = Client()

    def test_account_page_for_staff(self):
        self.client.login(username="admin", password="admin")
        res = self.client.get(reverse("staff:account"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Change username")
        self.assertContains(res, "Change password")

    def test_change_username(self):
        self.client.login(username="admin", password="admin")
        res = self.client.post(
            reverse("staff:account_username"),
            {"username": "mainadmin"},
        )
        self.assertEqual(res.status_code, 302)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.username, "mainadmin")

    def test_change_password(self):
        self.client.login(username="admin", password="admin")
        res = self.client.post(
            reverse("staff:account_password"),
            {
                "old_password": "admin",
                "new_password1": "NewComplexPass456!",
                "new_password2": "NewComplexPass456!",
            },
        )
        self.assertEqual(res.status_code, 302)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("NewComplexPass456!"))

    def test_team_list_requires_permission(self):
        self.client.login(username="editor", password="ComplexPass123!")
        res = self.client.get(reverse("staff:team_list"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("staff:dashboard"))

    def test_superuser_can_create_admin_with_permissions(self):
        self.client.login(username="admin", password="admin")
        res = self.client.post(
            reverse("staff:team_add"),
            {
                "username": "newadmin",
                "password1": "ComplexPass789!",
                "password2": "ComplexPass789!",
                "can_manage_books": "on",
                "can_manage_authors": "on",
                "can_manage_categories": "",
                "can_view_saved": "",
                "can_manage_team": "",
            },
        )
        self.assertEqual(res.status_code, 302)
        user = User.objects.get(username="newadmin")
        self.assertTrue(user.is_staff)
        profile = user.staff_profile
        self.assertTrue(profile.can_manage_books)
        self.assertTrue(profile.can_manage_authors)
        self.assertFalse(profile.can_manage_categories)
        self.assertFalse(profile.can_manage_team)

    def test_editor_blocked_from_authors(self):
        self.client.login(username="editor", password="ComplexPass123!")
        res = self.client.get(reverse("staff:author_list"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("staff:dashboard"))

    def test_editor_can_open_books(self):
        self.client.login(username="editor", password="ComplexPass123!")
        res = self.client.get(reverse("staff:book_list"))
        self.assertEqual(res.status_code, 200)

    def test_get_staff_access_superuser(self):
        access = get_staff_access(self.admin)
        self.assertTrue(access.can_manage_team)
        self.assertTrue(access.can_manage_books)
