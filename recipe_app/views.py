"""
Views for recipe APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core_app.models import Recipe
from recipe_app.serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    view for manage recipe APIs.
    """

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        """
        Retrieve recipes for authenticated user only.
        """

        return self.queryset.filter(user=self.request.user).order_by("-id")
    

