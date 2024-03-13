from django.urls import path

from . import views

urlpatterns = [
    path("api/login", views.loginUser, name="login"),
    path("api/logout", views.logoutUser, name="logout"),
    path("api/stories", views.post_or_get_article, name="post_or_get_article"),
    path("api/stories/<int:key>", views.delete_article, name="delete_article"),
]