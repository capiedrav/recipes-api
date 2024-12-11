"""
Views for recipe APIs.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core_app.models import Recipe, Tag, Ingredient
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    view for manage recipe APIs.
    """

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        """
        Retrieve recipes for authenticated user only.
        """

        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """
        Return the serializer class for requests.
        """

        if self.action == "list": # change serializer for listing action
            return RecipeSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new recipe.
        """
                
        serializer.save(user=self.request.user)


class BaseRecipeAttributesViewSet(viewsets.ModelViewSet):
    """
    Base class for Recipe attributes (i.e., tags, ingredients).
    """

    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        """
        Filter queryset to the authenticated user.
        """

        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """
        Create a new tag.
        """

        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttributesViewSet):
    """
    View to manage tags API.
    """

    serializer_class = TagSerializer
    queryset = Tag.objects.all()   
    

class IngredientViewSet(BaseRecipeAttributesViewSet):
    """
    View to manage ingredient API.
    """

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    