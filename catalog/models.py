from django.conf import settings
from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "author"
        verbose_name_plural = "authors"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("catalog:author_detail", kwargs={"slug": self.slug})


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    isbn = models.CharField(max_length=20, blank=True)
    published_date = models.DateField(null=True, blank=True)
    cover_url = models.URLField(
        blank=True,
        help_text="Public image URL used as the book cover on the site.",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured books appear on the home page.",
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="books"
    )
    authors = models.ManyToManyField(Author, related_name="books", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "book"
        verbose_name_plural = "books"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("catalog:book_detail", kwargs={"slug": self.slug})


class ReadingListItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_list",
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="on_shelves"
    )
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Your Shelter item"
        verbose_name_plural = "Your Shelter items"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"], name="unique_user_book_shelf"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.book}"
