from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse


class ShelterAdminSite(admin.AdminSite):
    """Friendlier admin hub for Your Shelter staff."""

    site_header = "Your Shelter Admin"
    site_title = "Your Shelter"
    index_title = "Welcome back"
    site_url = "/"
    enable_nav_sidebar = True

    def each_context(self, request):
        context = super().each_context(request)
        # Lazy import to avoid circular imports during app loading
        from .models import Author, Book, Category, ReadingListItem

        User = get_user_model()
        book_count = Book.objects.count()
        featured_count = Book.objects.filter(is_featured=True).count()
        context["shelter_stats"] = {
            "books": book_count,
            "featured": featured_count,
            "authors": Author.objects.count(),
            "categories": Category.objects.count(),
            "saved": ReadingListItem.objects.count(),
            "users": User.objects.count(),
            "missing_covers": Book.objects.filter(cover_url="").count(),
        }
        context["shelter_quick_links"] = [
            {
                "label": "Add a book",
                "url": reverse("admin:catalog_book_add"),
                "hint": "Title, cover, authors, category",
                "icon": "book",
            },
            {
                "label": "All books",
                "url": reverse("admin:catalog_book_changelist"),
                "hint": "Edit, feature, search",
                "icon": "list",
            },
            {
                "label": "Authors",
                "url": reverse("admin:catalog_author_changelist"),
                "hint": "Writers in the catalog",
                "icon": "author",
            },
            {
                "label": "Categories",
                "url": reverse("admin:catalog_category_changelist"),
                "hint": "Theology, devotional…",
                "icon": "tag",
            },
            {
                "label": "Saved books",
                "url": reverse("admin:catalog_readinglistitem_changelist"),
                "hint": "What readers saved",
                "icon": "heart",
            },
            {
                "label": "View public site",
                "url": "/",
                "hint": "Open the catalog in a new tab",
                "icon": "site",
                "external": True,
            },
        ]
        context["shelter_tips"] = [
            "Start with a Category, then an Author, then add Books.",
            "Slug fills in automatically from the title — you can edit it if needed.",
            "Paste a cover image URL to show a real cover on the site.",
            "Check Featured to put a book on the home page.",
            "Use the search box on any list page to find items fast.",
        ]
        return context


# name="admin" keeps reverse("admin:…") and login URLs working as usual
shelter_admin_site = ShelterAdminSite(name="admin")
