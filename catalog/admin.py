from django.contrib import admin

from .models import Author, Book, Category, ReadingListItem


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "bio")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_featured", "published_date")
    list_filter = ("is_featured", "category", "published_date")
    search_fields = ("title", "subtitle", "description", "isbn")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("authors",)
    autocomplete_fields = ("category",)


@admin.register(ReadingListItem)
class ReadingListItemAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "book__title")
    raw_id_fields = ("user", "book")
