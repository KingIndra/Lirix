from django.urls import path
from . import views

urlpatterns = [
    # LIST VIEWS
    path('poetry/', views.poetry, name="Poetry"),
    path('photography/', views.photography, name="Photography"),

    # CRUD URLS FOR POETRY
    path('poetry/new/', views.poetry_create, name="PoetryCreate"),
    path('poetry/<int:post_id>/', views.poetry_detail, name="PoetryDetail"),
    path('poetry/update/<int:post_id>/', views.poetry_update, name="PoetryUpdate"),
    path('poetry/delete/<int:post_id>/', views.poetry_delete, name="PoetryDelete"),

    # POETRY
    path('poetry/like/<int:post_id>/', views.poetry_like, name="PoetryLike"),
    path('poetry/likes_comments/<int:post_id>/', views.likes_comments, name="PoetryLikeCommentsCount"),
    path('poetry/comment/<int:post_id>/', views.poetry_comment_create, name="PoetryCommentCreate"),
    path('poetry/comment/update/<int:comment_id>/', views.poetry_comment_update, name="PoetryCommentUpdate"),
    path('poetry/comment/delete/<int:comment_id>/', views.poetry_comment_delete, name="PoetryCommentDelete"),

    # CRUD URLS FOR PHOTOGRAPHY
]