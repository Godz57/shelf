from django.db.models import Q
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Book

EASTER_BOOK = {
    "id": 0,
    "title": "The Quiet Room",
    "slug": "the-quiet-room",
    "subtitle": "A page that is not on any shelf",
    "description": (
        "You found what only the curious find. "
        "This hidden title is a gentle nod to readers who open the API. "
        "Shelter was built with Django — still has secrets."
    ),
    "isbn": "",
    "published_date": None,
    "cover_url": "",
    "is_featured": False,
    "category": "Hidden",
    "authors": ["The Keeper"],
    "hidden": True,
}


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    category = serializers.StringRelatedField()
    category_slug = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "slug",
            "subtitle",
            "description",
            "isbn",
            "published_date",
            "cover_url",
            "is_featured",
            "category",
            "category_slug",
            "authors",
        ]


class BookPagination(PageNumberPagination):
    page_size = 12


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.select_related("category").prefetch_related("authors")
    serializer_class = BookSerializer
    pagination_class = BookPagination
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(subtitle__icontains=q)
                | Q(description__icontains=q)
                | Q(authors__name__icontains=q)
            ).distinct()
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        easter = (request.query_params.get("easter") or "").strip().lower()
        if easter in {"1", "true", "yes"} and isinstance(response.data, dict):
            results = list(response.data.get("results") or [])
            results.append(dict(EASTER_BOOK))
            response.data["results"] = results
            if "count" in response.data:
                response.data["count"] = response.data["count"] + 1
        return response

    @action(detail=False, methods=["get"], url_path="pick")
    def pick(self, request):
        book = self.get_queryset().order_by("?").first()
        if book is None:
            return Response(
                {"detail": "No books in the catalog."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(self.get_serializer(book).data)
