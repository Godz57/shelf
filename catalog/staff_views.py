from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from .models import Author, Book, Category, ReadingListItem
from .slug_utils import unique_slug
from .staff_forms import AuthorForm, BookForm, CategoryForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only staff/superusers can manage the catalog."""

    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "You need staff access to open the manage panel.",
            )
            return redirect("catalog:home")
        return super().handle_no_permission()


class ManageDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "staff/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stats"] = {
            "books": Book.objects.count(),
            "featured": Book.objects.filter(is_featured=True).count(),
            "authors": Author.objects.count(),
            "categories": Category.objects.count(),
            "saved": ReadingListItem.objects.count(),
            "missing_covers": Book.objects.filter(cover_url="").count(),
        }
        ctx["recent_books"] = Book.objects.select_related("category").prefetch_related(
            "authors"
        )[:6]
        return ctx


class ManageBookListView(StaffRequiredMixin, ListView):
    model = Book
    template_name = "staff/book_list.html"
    context_object_name = "books"
    paginate_by = 12

    def get_queryset(self):
        qs = Book.objects.select_related("category").prefetch_related("authors")
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(subtitle__icontains=q)
                | Q(authors__name__icontains=q)
            ).distinct()
        category = (self.request.GET.get("category") or "").strip()
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["category_slug"] = (self.request.GET.get("category") or "").strip()
        ctx["categories"] = Category.objects.all()
        return ctx


class ManageBookCreateView(StaffRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "staff/book_form.html"

    def form_valid(self, form):
        book = form.save(commit=False)
        book.slug = unique_slug(Book, book.title)
        book.save()
        form.save_m2m()
        messages.success(self.request, f'“{book.title}” was added to the catalog.')
        return redirect("staff:book_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Add book"
        ctx["submit_label"] = "Save book"
        return ctx


class ManageBookUpdateView(StaffRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "staff/book_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        book = form.save(commit=False)
        book.slug = unique_slug(Book, book.title, instance=book)
        book.save()
        form.save_m2m()
        messages.success(self.request, f'“{book.title}” was updated.')
        return redirect("staff:book_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Edit book"
        ctx["submit_label"] = "Save changes"
        return ctx


class ManageBookDeleteView(StaffRequiredMixin, DeleteView):
    model = Book
    template_name = "staff/book_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("staff:book_list")

    def form_valid(self, form):
        title = self.object.title
        response = super().form_valid(form)
        messages.success(self.request, f'“{title}” was removed from the catalog.')
        return response


class ManageAuthorListView(StaffRequiredMixin, ListView):
    model = Author
    template_name = "staff/author_list.html"
    context_object_name = "authors"

    def get_queryset(self):
        return Author.objects.annotate(book_count=Count("books")).order_by("name")


class ManageAuthorCreateView(StaffRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = "staff/author_form.html"
    success_url = reverse_lazy("staff:author_list")

    def form_valid(self, form):
        author = form.save(commit=False)
        author.slug = unique_slug(Author, author.name)
        author.save()
        messages.success(self.request, f'Author “{author.name}” was added.')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Add author"
        ctx["submit_label"] = "Save author"
        return ctx


class ManageAuthorUpdateView(StaffRequiredMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = "staff/author_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("staff:author_list")

    def form_valid(self, form):
        author = form.save(commit=False)
        author.slug = unique_slug(Author, author.name, instance=author)
        author.save()
        messages.success(self.request, f'Author “{author.name}” was updated.')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Edit author"
        ctx["submit_label"] = "Save changes"
        return ctx


class ManageAuthorDeleteView(StaffRequiredMixin, DeleteView):
    model = Author
    template_name = "staff/author_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("staff:author_list")

    def form_valid(self, form):
        name = self.object.name
        # Block delete if books still reference (M2M is fine, but PROTECT not on M2M)
        response = super().form_valid(form)
        messages.success(self.request, f'Author “{name}” was removed.')
        return response


class ManageCategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = "staff/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(book_count=Count("books")).order_by("name")


class ManageCategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "staff/category_form.html"
    success_url = reverse_lazy("staff:category_list")

    def form_valid(self, form):
        cat = form.save(commit=False)
        cat.slug = unique_slug(Category, cat.name)
        cat.save()
        messages.success(self.request, f'Category “{cat.name}” was added.')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Add category"
        ctx["submit_label"] = "Save category"
        return ctx


class ManageCategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "staff/category_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("staff:category_list")

    def form_valid(self, form):
        cat = form.save(commit=False)
        cat.slug = unique_slug(Category, cat.name, instance=cat)
        cat.save()
        messages.success(self.request, f'Category “{cat.name}” was updated.')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Edit category"
        ctx["submit_label"] = "Save changes"
        return ctx


class ManageCategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "staff/category_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("staff:category_list")

    def form_valid(self, form):
        if self.object.books.exists():
            messages.error(
                self.request,
                f'Cannot delete “{self.object.name}” while books still use it. '
                "Move those books to another category first.",
            )
            return redirect("staff:category_list")
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Category “{name}” was removed.')
        return response


class ManageSavedListView(StaffRequiredMixin, ListView):
    model = ReadingListItem
    template_name = "staff/saved_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        return ReadingListItem.objects.select_related(
            "user", "book", "book__category"
        )
