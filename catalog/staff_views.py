from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .models import Author, Book, Category, ReadingListItem
from .permissions import ensure_staff_profile, get_staff_access
from .slug_utils import unique_slug
from .staff_forms import (
    AuthorForm,
    BookForm,
    CategoryForm,
    StaffPasswordChangeForm,
    StaffUserCreateForm,
    StaffUserEditForm,
    UsernameChangeForm,
)

User = get_user_model()


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Logged-in staff only."""

    login_url = reverse_lazy("login")
    staff_permission = None  # e.g. "can_manage_books"

    def test_func(self):
        user = self.request.user
        if not (user.is_authenticated and user.is_staff):
            return False
        if self.staff_permission is None:
            return True
        access = get_staff_access(user)
        return getattr(access, self.staff_permission, False)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff and self.staff_permission:
                messages.error(
                    self.request,
                    "You do not have access to that section. Ask a team admin.",
                )
                return redirect("staff:dashboard")
            messages.error(
                self.request,
                "You need staff access to open the manage panel.",
            )
            return redirect("catalog:home")
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["staff_access"] = get_staff_access(self.request.user)
        return ctx


class ManageDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "staff/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        access = ctx["staff_access"]
        ctx["stats"] = {
            "books": Book.objects.count(),
            "featured": Book.objects.filter(is_featured=True).count(),
            "authors": Author.objects.count(),
            "categories": Category.objects.count(),
            "saved": ReadingListItem.objects.count(),
            "missing_covers": Book.objects.filter(cover_url="").count(),
            "team": User.objects.filter(is_staff=True).count(),
        }
        if access.can_manage_books:
            ctx["recent_books"] = Book.objects.select_related(
                "category"
            ).prefetch_related("authors")[:6]
        else:
            ctx["recent_books"] = []
        return ctx


class ManageBookListView(StaffRequiredMixin, ListView):
    model = Book
    template_name = "staff/book_list.html"
    context_object_name = "books"
    paginate_by = 12
    staff_permission = "can_manage_books"

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
    staff_permission = "can_manage_books"

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
    staff_permission = "can_manage_books"

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
    staff_permission = "can_manage_books"

    def form_valid(self, form):
        title = self.object.title
        response = super().form_valid(form)
        messages.success(self.request, f'“{title}” was removed from the catalog.')
        return response


class ManageAuthorListView(StaffRequiredMixin, ListView):
    model = Author
    template_name = "staff/author_list.html"
    context_object_name = "authors"
    staff_permission = "can_manage_authors"

    def get_queryset(self):
        return Author.objects.annotate(book_count=Count("books")).order_by("name")


class ManageAuthorCreateView(StaffRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = "staff/author_form.html"
    success_url = reverse_lazy("staff:author_list")
    staff_permission = "can_manage_authors"

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
    staff_permission = "can_manage_authors"

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
    staff_permission = "can_manage_authors"

    def form_valid(self, form):
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Author “{name}” was removed.')
        return response


class ManageCategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = "staff/category_list.html"
    context_object_name = "categories"
    staff_permission = "can_manage_categories"

    def get_queryset(self):
        return Category.objects.annotate(book_count=Count("books")).order_by("name")


class ManageCategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "staff/category_form.html"
    success_url = reverse_lazy("staff:category_list")
    staff_permission = "can_manage_categories"

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
    staff_permission = "can_manage_categories"

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
    staff_permission = "can_manage_categories"

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
    staff_permission = "can_view_saved"

    def get_queryset(self):
        return ReadingListItem.objects.select_related(
            "user", "book", "book__category"
        )


# —— Account (any staff) ——


class ManageAccountView(StaffRequiredMixin, TemplateView):
    template_name = "staff/account.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["username_form"] = UsernameChangeForm(user=user)
        ctx["password_form"] = StaffPasswordChangeForm(user=user)
        ctx["access"] = get_staff_access(user)
        return ctx


class ManageUsernameUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        form = UsernameChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your username was updated.")
        else:
            for err in form.errors.values():
                messages.error(request, err.as_text())
        return redirect("staff:account")


class ManagePasswordUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        form = StaffPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was updated.")
        else:
            for field_errors in form.errors.values():
                for err in field_errors:
                    messages.error(request, err)
        return redirect("staff:account")


# —— Team (only can_manage_team) ——


class ManageTeamListView(StaffRequiredMixin, ListView):
    template_name = "staff/team_list.html"
    context_object_name = "staff_users"
    staff_permission = "can_manage_team"

    def get_queryset(self):
        qs = (
            User.objects.filter(is_staff=True)
            .select_related("staff_profile")
            .order_by("username")
        )
        for user in qs:
            ensure_staff_profile(user)
        return qs



class ManageTeamCreateView(StaffRequiredMixin, FormView):
    template_name = "staff/team_form.html"
    form_class = StaffUserCreateForm
    staff_permission = "can_manage_team"
    success_url = reverse_lazy("staff:team_list")

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            f'Admin “{user.username}” was created. They can log in with that username.',
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Add admin"
        ctx["submit_label"] = "Create admin"
        return ctx


class ManageTeamEditView(StaffRequiredMixin, FormView):
    template_name = "staff/team_form.html"
    form_class = StaffUserEditForm
    staff_permission = "can_manage_team"

    def dispatch(self, request, *args, **kwargs):
        self.edit_user = get_object_or_404(User, pk=kwargs["pk"], is_staff=True)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.edit_user
        return kwargs

    def form_valid(self, form):
        # Prevent locking yourself out of team management carelessly
        if self.edit_user.pk == self.request.user.pk:
            if not form.cleaned_data.get("is_active", True):
                messages.error(self.request, "You cannot deactivate your own account.")
                return redirect("staff:team_edit", pk=self.edit_user.pk)
            if not self.request.user.is_superuser and not form.cleaned_data.get(
                "can_manage_team"
            ):
                messages.error(
                    self.request,
                    "You cannot remove your own Team & permissions access.",
                )
                return redirect("staff:team_edit", pk=self.edit_user.pk)
        form.save()
        messages.success(
            self.request, f'Admin “{self.edit_user.username}” was updated.'
        )
        return redirect("staff:team_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = f"Edit admin · {self.edit_user.username}"
        ctx["submit_label"] = "Save changes"
        ctx["edit_user"] = self.edit_user
        return ctx
