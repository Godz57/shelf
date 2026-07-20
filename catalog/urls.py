from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("health/", views.health, name="health"),
    path("books/", views.book_list, name="book_list"),
    path("books/<slug:slug>/", views.book_detail, name="book_detail"),
    path("authors/<slug:slug>/", views.author_detail, name="author_detail"),
    path("accounts/signup/", views.signup, name="signup"),
    path("your-shelter/", views.my_shelf, name="my_shelf"),
    path("your-shelter/add/<int:book_id>/", views.shelf_add, name="shelf_add"),
    path("your-shelter/remove/<int:book_id>/", views.shelf_remove, name="shelf_remove"),
    # Template smoke for 500 page (not linked in nav)
    path("__500__/", views.server_error_demo, name="server_error_demo"),
]
