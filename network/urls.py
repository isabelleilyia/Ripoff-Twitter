
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create",views.create, name="create"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow/<str:username>", views.follow, name="follow"),
    path("following", views.following_posts, name="following"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("like", views.update_like, name="like")
]
