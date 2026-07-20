from django.urls import path

from . import staff_views

app_name = "staff"

urlpatterns = [
    path("", staff_views.ManageDashboardView.as_view(), name="dashboard"),
    path("account/", staff_views.ManageAccountView.as_view(), name="account"),
    path(
        "account/username/",
        staff_views.ManageUsernameUpdateView.as_view(),
        name="account_username",
    ),
    path(
        "account/password/",
        staff_views.ManagePasswordUpdateView.as_view(),
        name="account_password",
    ),
    path("team/", staff_views.ManageTeamListView.as_view(), name="team_list"),
    path("team/new/", staff_views.ManageTeamCreateView.as_view(), name="team_add"),
    path(
        "team/<int:pk>/edit/",
        staff_views.ManageTeamEditView.as_view(),
        name="team_edit",
    ),
    path("books/", staff_views.ManageBookListView.as_view(), name="book_list"),
    path("books/new/", staff_views.ManageBookCreateView.as_view(), name="book_add"),
    path(
        "books/<slug:slug>/edit/",
        staff_views.ManageBookUpdateView.as_view(),
        name="book_edit",
    ),
    path(
        "books/<slug:slug>/delete/",
        staff_views.ManageBookDeleteView.as_view(),
        name="book_delete",
    ),
    path("authors/", staff_views.ManageAuthorListView.as_view(), name="author_list"),
    path(
        "authors/new/",
        staff_views.ManageAuthorCreateView.as_view(),
        name="author_add",
    ),
    path(
        "authors/<slug:slug>/edit/",
        staff_views.ManageAuthorUpdateView.as_view(),
        name="author_edit",
    ),
    path(
        "authors/<slug:slug>/delete/",
        staff_views.ManageAuthorDeleteView.as_view(),
        name="author_delete",
    ),
    path(
        "categories/",
        staff_views.ManageCategoryListView.as_view(),
        name="category_list",
    ),
    path(
        "categories/new/",
        staff_views.ManageCategoryCreateView.as_view(),
        name="category_add",
    ),
    path(
        "categories/<slug:slug>/edit/",
        staff_views.ManageCategoryUpdateView.as_view(),
        name="category_edit",
    ),
    path(
        "categories/<slug:slug>/delete/",
        staff_views.ManageCategoryDeleteView.as_view(),
        name="category_delete",
    ),
    path("saved/", staff_views.ManageSavedListView.as_view(), name="saved_list"),
]
