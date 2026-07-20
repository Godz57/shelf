from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Author, Book, Category, ReadingListItem

# Brand the admin chrome
admin.site.site_header = "Your Shelter Admin"
admin.site.site_title = "Your Shelter"
admin.site.index_title = "Catalog management"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "book_count", "created_at")
    list_display_links = ("name",)
    search_fields = ("name", "bio")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("name", "slug")}),
        ("Biography", {"fields": ("bio",)}),
        ("Meta", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    @admin.display(description="Books")
    def book_count(self, obj: Author) -> int:
        return obj.books.count()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "book_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Books")
    def book_count(self, obj: Category) -> int:
        return obj.books.count()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "category",
        "author_list",
        "is_featured",
        "published_date",
        "created_at",
    )
    list_display_links = ("title",)
    list_filter = ("is_featured", "category", "published_date")
    list_editable = ("is_featured",)
    search_fields = ("title", "subtitle", "description", "isbn", "authors__name")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("authors",)
    autocomplete_fields = ("category",)
    date_hierarchy = "published_date"
    ordering = ("-created_at",)
    list_per_page = 25
    save_on_top = True
    readonly_fields = ("created_at", "cover_preview", "view_on_site_link")

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "title",
                    "slug",
                    "subtitle",
                    "category",
                    "authors",
                    "is_featured",
                )
            },
        ),
        (
            "Cover",
            {
                "fields": ("cover_url", "cover_preview"),
                "description": "Paste a public image URL (Unsplash, CDN, etc.).",
            },
        ),
        (
            "Content",
            {"fields": ("description", "isbn", "published_date")},
        ),
        (
            "Meta",
            {
                "fields": ("created_at", "view_on_site_link"),
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
            '<span class="shelter-cover-fallback">{}</span>',
            initial,
        )

    @admin.display(description="Cover preview")
    def cover_preview(self, obj: Book) -> str:
        if not obj.pk:
            return mark_safe("<em>Save the book to preview the cover.</em>")
        if obj.cover_url:
            return format_html(
                '<img src="{}" alt="Cover of {}" class="shelter-cover-preview" />',
                obj.cover_url,
                obj.title,
            )
        return mark_safe(
            "<em>No cover URL yet — the public site will show a gradient initial.</em>"
        )

    @admin.display(description="Authors")
    def author_list(self, obj: Book) -> str:
        names = list(obj.authors.values_list("name", flat=True)[:4])
        if not names:
            return "—"
        text = ", ".join(names)
        extra = obj.authors.count() - len(names)
        if extra > 0:
            text = f"{text} +{extra}"
        return text

    @admin.display(description="Public page")
    def view_on_site_link(self, obj: Book) -> str:
        if not obj.pk:
            return "—"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Open on site ↗</a>',
            obj.get_absolute_url(),
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("authors")
        )


@admin.register(ReadingListItem)
class ReadingListItemAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "notes_short", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "book__title", "notes")
    autocomplete_fields = ("user", "book")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("user", "book", "notes")}),
        ("Meta", {"fields": ("created_at",), "classes": ("collapse",)}),
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
