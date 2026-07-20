from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("books/<slug:slug>/", views.book_detail, name="book_detail"),
    path("authors/<slug:slug>/", views.author_detail, name="author_detail"),
    path("accounts/signup/", views.signup, name="signup"),
    path("my-shelter/", views.my_shelf, name="my_shelf"),
    path("my-shelter/add/<int:book_id>/", views.shelf_add, name="shelf_add"),
    path("my-shelter/remove/<int:book_id>/", views.shelf_remove, name="shelf_remove"),
]
