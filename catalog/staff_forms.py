from django import forms

from .models import Author, Book, Category


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "subtitle",
            "category",
            "authors",
            "description",
            "cover_url",
            "is_featured",
            "isbn",
            "published_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Book title"}),
            "subtitle": forms.TextInput(attrs={"placeholder": "Optional subtitle"}),
            "description": forms.Textarea(attrs={"rows": 6, "placeholder": "Short description for readers"}),
            "cover_url": forms.URLInput(attrs={"placeholder": "https://…"}),
            "isbn": forms.TextInput(attrs={"placeholder": "Optional"}),
            "published_date": forms.DateInput(attrs={"type": "date"}),
            "authors": forms.CheckboxSelectMultiple,
        }
        labels = {
            "title": "Title",
            "subtitle": "Subtitle (optional)",
            "category": "Category",
            "authors": "Authors",
            "description": "Description",
            "cover_url": "Cover image link (optional)",
            "is_featured": "Feature on home page",
            "isbn": "ISBN (optional)",
            "published_date": "Publication date (optional)",
        }
        help_texts = {
            "cover_url": "Paste a full image URL starting with https://",
            "is_featured": "Show this book in the Featured section on the home page.",
            "authors": "Select one or more authors. Create the author first if needed.",
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["name", "bio"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Author name"}),
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional short bio"}),
        }
        labels = {
            "name": "Name",
            "bio": "Bio (optional)",
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Theology, Devotional"}),
        }
        labels = {"name": "Category name"}
