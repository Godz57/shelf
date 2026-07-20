from django.test import TestCase, override_settings
from django.urls import reverse


class SecurityAndHealthTests(TestCase):
    def test_health_json(self):
        res = self.client.get(reverse("catalog:health"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"].split(";")[0], "application/json")
        self.assertEqual(res.json(), {"status": "ok"})

    @override_settings(
        DEBUG=False,
        SECURE_CONTENT_TYPE_NOSNIFF=True,
        X_FRAME_OPTIONS="DENY",
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
    )
    def test_security_headers_on_home(self):
        res = self.client.get(reverse("catalog:home"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.get("X-Frame-Options"), "DENY")
