"""
Views for recipe APIs.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core_app.models import Recipe, Tag
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer


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


# class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet): # don't know why use this instead of viewset.ModelViewset
class TagViewSet(viewsets.ModelViewSet):
    """
    View for Manage tags API.
    """

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        """
        Filter queryset to the authenticated user.
        """

        return self.queryset.filter(user=self.request.user).order_by("-name")
    