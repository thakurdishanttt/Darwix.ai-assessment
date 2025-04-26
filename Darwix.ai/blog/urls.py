from django.urls import path
from .views import blog_suggest

urlpatterns = [
    path('bloges/<str:title>/', blog_suggest, name='blog_suggest'),
]
