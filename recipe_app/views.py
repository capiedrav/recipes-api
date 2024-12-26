"""
Views for recipe APIs.
"""

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, \
     OpenApiParameter, OpenApiTypes
from core_app.models import Recipe, Tag, Ingredient
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer, \
     TagSerializer, IngredientSerializer, RecipeImageSerializer

# decorate RecipeViewSet class to document tags and ingredients params in swagger browsable API
@extend_schema_view(
    list=extend_schema( # this only applies to the recipe-list endpoint
        parameters=[
            OpenApiParameter(
                name="tags", 
                type=OpenApiTypes.STR,
                description="Comma separated list of tag ids to filter"
            ),
            OpenApiParameter(
                name="ingredients",
                type=OpenApiTypes.STR,
                description="Comma separated list of ingredient ids to filter"
            )

        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """
    view for manage recipe APIs.
    """

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def _params_to_ints(self, params):
        """
        Convert params (a list of strings) to a list of ints.
        """

        return [int(str_id) for str_id in params.split(",")]

    def get_queryset(self):
        """
        Retrieve recipes for authenticated user only.
        """
        
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")

        if tags:
            tag_ids = self._params_to_ints(tags)
            self.queryset = self.queryset.filter(tags__id__in=tag_ids)
        
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            self.queryset = self.queryset.filter(ingredients__id__in=ingredient_ids)

        return self.queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        """
        Return the serializer class for requests.
        """

        if self.action == "list": # change serializer for listing action
            return RecipeSerializer
        elif self.action == "upload_image":
            return RecipeImageSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new recipe.
        """
                
        serializer.save(user=self.request.user)

    @action(methods=["POST", ], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """
        Upload a recipe image.
        """

        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        




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
    