"""
Views for recipe APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core_app.models import Recipe
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer


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



    

