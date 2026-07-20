from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .admin_site import shelter_admin_site
from .models import Author, Book, Category, ReadingListItem


@admin.register(Author, site=shelter_admin_site)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "book_count", "created_at")
    list_display_links = ("name",)
    search_fields = ("name", "bio")
    search_help_text = "Search by author name or bio text."
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)
    ordering = ("name",)
    list_per_page = 30
    empty_value_display = "—"
    fieldsets = (
        (
            "Who is this author?",
            {
                "description": "Name appears on book pages. The slug is used in the URL.",
                "fields": ("name", "slug"),
            },
        ),
        (
            "About them",
            {
                "description": "Optional short bio for the public author page.",
                "fields": ("bio",),
            },
        ),
        (
            "System info",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Books in catalog")
    def book_count(self, obj: Author) -> int:
        return obj.books.count()


@admin.register(Category, site=shelter_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "book_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    search_help_text = "Search categories by name."
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    empty_value_display = "—"
    fieldsets = (
        (
            "Category",
            {
                "description": (
                    "Categories group books on the public catalog "
                    "(e.g. Theology, Devotional)."
                ),
                "fields": ("name", "slug"),
            },
        ),
    )

    @admin.display(description="Books in catalog")
    def book_count(self, obj: Category) -> int:
        return obj.books.count()


@admin.register(Book, site=shelter_admin_site)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "category",
        "author_list",
        "is_featured",
        "has_cover",
        "published_date",
    )
    list_display_links = ("title",)
    list_filter = ("is_featured", "category", "published_date")
    list_editable = ("is_featured",)
    search_fields = ("title", "subtitle", "description", "isbn", "authors__name")
    search_help_text = "Search by title, subtitle, author name, or ISBN."
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("authors",)
    autocomplete_fields = ("category",)
    date_hierarchy = "published_date"
    ordering = ("-created_at",)
    list_per_page = 20
    list_max_show_all = 100
    save_on_top = True
    empty_value_display = "—"
    actions = ("make_featured", "remove_featured", "clear_cover_urls")
    readonly_fields = ("created_at", "cover_preview", "view_on_site_link", "how_it_works")

    fieldsets = (
        (
            "1 · Basic info",
            {
                "description": (
                    "What readers see first. Slug becomes the URL "
                    "(e.g. /books/grace-and-truth/)."
                ),
                "fields": (
                    "title",
                    "slug",
                    "subtitle",
                    "category",
                    "authors",
                    "is_featured",
                ),
            },
        ),
        (
            "2 · Cover image",
            {
                "description": (
                    "Paste a full image URL (https://…). "
                    "Unsplash and similar CDNs work well. "
                    "Leave empty for a simple letter placeholder."
                ),
                "fields": ("cover_url", "cover_preview"),
            },
        ),
        (
            "3 · Description & details",
            {
                "description": "Description appears on the book detail page.",
                "fields": ("description", "isbn", "published_date"),
            },
        ),
        (
            "Help & links",
            {
                "fields": ("how_it_works", "view_on_site_link", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Cover")
    def cover_thumb(self, obj: Book) -> str:
        if obj.cover_url:
            return format_html(
                '<img src="{}" alt="" class="shelter-cover-thumb" width="40" height="60" />',
                obj.cover_url,
            )
        initial = (obj.title[:1] or "?").upper()
        return format_html(
            '<span class="shelter-cover-fallback" title="No cover URL">{}</span>',
            initial,
        )

    @admin.display(description="Cover?", boolean=True)
    def has_cover(self, obj: Book) -> bool:
        return bool(obj.cover_url)

    @admin.display(description="Preview")
    def cover_preview(self, obj: Book) -> str:
        if not obj.pk:
            return mark_safe(
                '<p class="shelter-help-box">Save this book once, then reopen to preview the cover.</p>'
            )
        if obj.cover_url:
            return format_html(
                '<img src="{}" alt="Cover of {}" class="shelter-cover-preview" />'
                '<p class="shelter-help-muted">Looks good? Readers see this on the public site.</p>',
                obj.cover_url,
                obj.title,
            )
        return mark_safe(
            '<p class="shelter-help-box">No cover yet — the site will show a colored tile with the first letter.</p>'
        )

    @admin.display(description="Authors")
    def author_list(self, obj: Book) -> str:
        names = list(obj.authors.values_list("name", flat=True)[:4])
        if not names:
            return "— (add authors below)"
        text = ", ".join(names)
        extra = obj.authors.count() - len(names)
        if extra > 0:
            text = f"{text} +{extra}"
        return text

    @admin.display(description="Public page")
    def view_on_site_link(self, obj: Book) -> str:
        if not obj.pk:
            return "Save first to open the public page."
        return format_html(
            '<a class="shelter-btn-link" href="{}" target="_blank" rel="noopener">'
            "Open this book on the site ↗</a>",
            obj.get_absolute_url(),
        )

    @admin.display(description="Quick guide")
    def how_it_works(self, obj: Book) -> str:
        return mark_safe(
            '<ol class="shelter-howto">'
            "<li>Fill title, category, and at least one author.</li>"
            "<li>Paste a cover URL if you have one.</li>"
            "<li>Write a short description readers will understand.</li>"
            "<li>Tick <strong>Featured</strong> to show it on the home page.</li>"
            "<li>Click <strong>Save</strong>, then use “Open on the site” to check.</li>"
            "</ol>"
        )

    @admin.action(description="Mark selected as Featured (home page)")
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(
            request,
            f"{updated} book(s) are now featured on the home page.",
        )

    @admin.action(description="Remove Featured from selected")
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"Featured removed from {updated} book(s).")

    @admin.action(description="Clear cover URLs from selected")
    def clear_cover_urls(self, request, queryset):
        updated = queryset.update(cover_url="")
        self.message_user(request, f"Cover URL cleared on {updated} book(s).")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("authors")
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Books — catalog"
        extra_context["shelter_list_hint"] = (
            "Tip: tick Featured in the list and click Save, "
            "or use the Actions menu for bulk changes."
        )
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ReadingListItem, site=shelter_admin_site)
class ReadingListItemAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "notes_short", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "book__title", "notes")
    search_help_text = "Search by username or book title."
    autocomplete_fields = ("user", "book")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    empty_value_display = "—"
    fieldsets = (
        (
            "Saved book",
            {
                "description": (
                    "These are books readers added to Your Shelter "
                    "(their personal reading list)."
                ),
                "fields": ("user", "book", "notes"),
            },
        ),
        (
            "When",
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Notes")
    def notes_short(self, obj: ReadingListItem) -> str:
        if not obj.notes:
            return "—"
        return obj.notes if len(obj.notes) <= 40 else f"{obj.notes[:37]}…"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "book", "book__category")
        )


# Auth models on the same friendly admin site
shelter_admin_site.register(User, UserAdmin)
shelter_admin_site.register(Group, GroupAdmin)
