from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password

from .models import Author, Book, Category, StaffProfile

User = get_user_model()


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
            "description": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Short description for readers"}
            ),
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
            "bio": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Optional short bio"}
            ),
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
            "name": forms.TextInput(
                attrs={"placeholder": "e.g. Theology, Devotional"}
            ),
        }
        labels = {"name": "Category name"}


class UsernameChangeForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        help_text="This is what you type when you log in.",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["username"].initial = user.username

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        qs = User.objects.filter(username__iexact=username).exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.save(update_fields=["username"])
        return self.user


class StaffPasswordChangeForm(PasswordChangeForm):
    """Same as Django’s, with friendlier labels."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Current password"
        self.fields["new_password1"].label = "New password"
        self.fields["new_password2"].label = "Confirm new password"


class StaffUserCreateForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="They can change this later in My account.",
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
    )
    can_manage_books = forms.BooleanField(label="Books", required=False, initial=True)
    can_manage_authors = forms.BooleanField(
        label="Authors", required=False, initial=True
    )
    can_manage_categories = forms.BooleanField(
        label="Categories", required=False, initial=True
    )
    can_view_saved = forms.BooleanField(
        label="Saved by readers", required=False, initial=True
    )
    can_manage_team = forms.BooleanField(
        label="Team & permissions",
        required=False,
        initial=False,
        help_text="Can add other admins and change access.",
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        if p1:
            validate_password(p1)
        return cleaned

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password1"],
        )
        user.is_staff = True
        user.is_active = True
        user.save(update_fields=["is_staff", "is_active"])
        StaffProfile.objects.update_or_create(
            user=user,
            defaults={
                "can_manage_books": self.cleaned_data["can_manage_books"],
                "can_manage_authors": self.cleaned_data["can_manage_authors"],
                "can_manage_categories": self.cleaned_data["can_manage_categories"],
                "can_view_saved": self.cleaned_data["can_view_saved"],
                "can_manage_team": self.cleaned_data["can_manage_team"],
            },
        )
        return user


class StaffUserEditForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    is_active = forms.BooleanField(
        label="Account active",
        required=False,
        help_text="Uncheck to block login without deleting the account.",
    )
    can_manage_books = forms.BooleanField(label="Books", required=False)
    can_manage_authors = forms.BooleanField(label="Authors", required=False)
    can_manage_categories = forms.BooleanField(label="Categories", required=False)
    can_view_saved = forms.BooleanField(label="Saved by readers", required=False)
    can_manage_team = forms.BooleanField(
        label="Team & permissions",
        required=False,
        help_text="Can add other admins and change access.",
    )
    new_password = forms.CharField(
        label="Set new password (optional)",
        required=False,
        widget=forms.PasswordInput,
        help_text="Leave blank to keep the current password.",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        profile = getattr(user, "staff_profile", None)
        self.fields["username"].initial = user.username
        self.fields["is_active"].initial = user.is_active
        if profile:
            self.fields["can_manage_books"].initial = profile.can_manage_books
            self.fields["can_manage_authors"].initial = profile.can_manage_authors
            self.fields["can_manage_categories"].initial = profile.can_manage_categories
            self.fields["can_view_saved"].initial = profile.can_view_saved
            self.fields["can_manage_team"].initial = profile.can_manage_team
        if user.is_superuser:
            # Superuser always full access — show as locked info via form note
            for key in (
                "can_manage_books",
                "can_manage_authors",
                "can_manage_categories",
                "can_view_saved",
                "can_manage_team",
            ):
                self.fields[key].disabled = True
                self.fields[key].initial = True

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username__iexact=username).exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password") or ""
        if password:
            validate_password(password, user=self.user)
        return password

    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.is_active = self.cleaned_data.get("is_active", False)
        # Never remove staff flag from superuser accidentally
        if not self.user.is_superuser:
            self.user.is_staff = True
        self.user.save()
        password = self.cleaned_data.get("new_password")
        if password:
            self.user.set_password(password)
            self.user.save(update_fields=["password"])
        if not self.user.is_superuser:
            StaffProfile.objects.update_or_create(
                user=self.user,
                defaults={
                    "can_manage_books": self.cleaned_data.get("can_manage_books", False),
                    "can_manage_authors": self.cleaned_data.get(
                        "can_manage_authors", False
                    ),
                    "can_manage_categories": self.cleaned_data.get(
                        "can_manage_categories", False
                    ),
                    "can_view_saved": self.cleaned_data.get("can_view_saved", False),
                    "can_manage_team": self.cleaned_data.get("can_manage_team", False),
                },
            )
        return self.user
