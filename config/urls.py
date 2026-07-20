from django.urls import include, path

from catalog.admin_site import shelter_admin_site

urlpatterns = [
    path("admin/", shelter_admin_site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include("catalog.api_urls")),
    path("", include("catalog.urls")),
]
