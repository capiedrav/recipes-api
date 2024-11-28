"""
URL mappings for the recipe API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagViewSet


app_name = "recipe_app"
router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("tags", TagViewSet)

urlpatterns = [
    path("", include(router.urls))
]

