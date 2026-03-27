from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    # Auth
    path(
        "accounts/login/",
        views.login_user,
        name="login",
    ),
    path(
        "accounts/logout/",
        views.logout_user,
        name="logout",
    ),
    path(
        "accounts/register/",
        views.register,
        name="register",
    ),
    # Posts
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/new/", views.PostCreateView.as_view(), name="post_create"),
    path(
        "post/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="post_update",
    ),
    path(
        "post/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    # Likes
    path(
        "post/<int:pk>/like/",
        views.toggle_like,
        name="post_like_toggle",
    ),
]

