from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    category = serializers.StringRelatedField()

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
            "authors",
        ]


class BookPagination(PageNumberPagination):
    page_size = 12


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.select_related("category").prefetch_related("authors")
    serializer_class = BookSerializer
    pagination_class = BookPagination
    lookup_field = "slug"
