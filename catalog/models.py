from django.conf import settings
from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField("display name", max_length=200)
    slug = models.SlugField(
        "URL slug",
        unique=True,
        help_text="Used in the author page URL. Auto-filled from the name.",
    )
    bio = models.TextField("short bio", blank=True, help_text="Optional. Shown on the author page.")
    created_at = models.DateTimeField("created", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "author"
        verbose_name_plural = "authors"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("catalog:author_detail", kwargs={"slug": self.slug})


class Category(models.Model):
    name = models.CharField("name", max_length=100)
    slug = models.SlugField(
        "URL slug",
        unique=True,
        help_text="Used in filters and URLs. Auto-filled from the name.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField("title", max_length=255)
    slug = models.SlugField(
        "URL slug",
        unique=True,
        help_text="Auto-filled from the title. Appears in /books/your-slug/.",
    )
    subtitle = models.CharField("subtitle", max_length=255, blank=True)
    description = models.TextField(
        "description",
        help_text="Main blurb on the book page. Keep it clear for readers.",
    )
    isbn = models.CharField("ISBN", max_length=20, blank=True)
    published_date = models.DateField(
        "publication date",
        null=True,
        blank=True,
        help_text="Optional. Format: YYYY-MM-DD.",
    )
    cover_url = models.URLField(
        "cover image URL",
        blank=True,
        help_text="Full https:// link to a cover image (Unsplash, CDN, etc.).",
    )
    is_featured = models.BooleanField(
        "featured on home page",
        default=False,
        help_text="Turn on to show this book in the Featured section of the home page.",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="category",
    )
    authors = models.ManyToManyField(
        Author,
        related_name="books",
        blank=True,
        verbose_name="authors",
        help_text="Hold Ctrl (Windows) or Cmd (Mac) to select more than one.",
    )
    created_at = models.DateTimeField("created", auto_now_add=True)

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
        verbose_name="reader",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="on_shelves",
        verbose_name="book",
    )
    notes = models.CharField(
        "private note",
        max_length=255,
        blank=True,
        help_text="Optional note from or about this saved book.",
    )
    created_at = models.DateTimeField("saved on", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "saved book"
        verbose_name_plural = "saved books"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"], name="unique_user_book_shelf"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.book}"
