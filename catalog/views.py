from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import SignUpForm
from .models import Author, Book, Category, ReadingListItem


def home(request):
    featured = Book.objects.filter(is_featured=True).prefetch_related("authors")[:6]
    recent = Book.objects.prefetch_related("authors")[:8]
    return render(
        request,
        "catalog/home.html",
        {"featured_books": featured, "recent_books": recent},
    )


def book_list(request):
    qs = Book.objects.select_related("category").prefetch_related("authors")
    q = (request.GET.get("q") or "").strip()
    category_slug = (request.GET.get("category") or "").strip()
    sort = (request.GET.get("sort") or "newest").strip()

    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(subtitle__icontains=q)
            | Q(description__icontains=q)
            | Q(authors__name__icontains=q)
        ).distinct()

    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    sort_map = {
        "newest": "-created_at",
        "oldest": "created_at",
        "title": "title",
        "title_desc": "-title",
    }
    qs = qs.order_by(sort_map.get(sort, "-created_at"))

    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "catalog/book_list.html",
        {
            "page_obj": page,
            "categories": Category.objects.all(),
            "q": q,
            "category_slug": category_slug,
            "sort": sort,
        },
    )


def book_detail(request, slug):
    book = get_object_or_404(
        Book.objects.select_related("category").prefetch_related("authors"),
        slug=slug,
    )
    on_shelf = False
    if request.user.is_authenticated:
        on_shelf = request.user.reading_list.filter(book=book).exists()
    return render(
        request,
        "catalog/book_detail.html",
        {"book": book, "on_shelf": on_shelf},
    )


def author_detail(request, slug):
    author = get_object_or_404(Author, slug=slug)
    books = author.books.select_related("category")
    return render(
        request,
        "catalog/author_detail.html",
        {"author": author, "books": books},
    )


def signup(request):
    if request.user.is_authenticated:
        return redirect("catalog:home")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("catalog:home")
    else:
        form = SignUpForm()
    return render(request, "catalog/signup.html", {"form": form})


@login_required
def my_shelf(request):
    items = (
        ReadingListItem.objects.filter(user=request.user)
        .select_related("book", "book__category")
        .prefetch_related("book__authors")
    )
    return render(request, "catalog/my_shelf.html", {"items": items})


@login_required
@require_POST
def shelf_add(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    ReadingListItem.objects.get_or_create(user=request.user, book=book)
    messages.success(request, f'Added “{book.title}” to your shelter.')
    next_url = request.POST.get("next") or book.get_absolute_url()
    return redirect(next_url)


@login_required
@require_POST
def shelf_remove(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    ReadingListItem.objects.filter(user=request.user, book=book).delete()
    messages.info(request, f'Removed “{book.title}” from your shelter.')
    next_url = request.POST.get("next") or reverse("catalog:my_shelf")
    return redirect(next_url)


def page_not_found(request, exception):
    """Friendly 404 for public site (handler404)."""
    return render(request, "404.html", status=404)
