from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Staff manage panel (site-styled CRUD) — primary admin UX
    path("manage/", include("catalog.staff_urls")),
    # Old Django Admin UI is hidden: anything under /admin/ goes to /manage/
    path(
        "admin/",
        RedirectView.as_view(pattern_name="staff:dashboard", permanent=False),
        name="admin_redirect",
    ),
    path(
        "admin/<path:unused>/",
        RedirectView.as_view(pattern_name="staff:dashboard", permanent=False),
        name="admin_redirect_subpath",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include("catalog.api_urls")),
    path("", include("catalog.urls")),
]
