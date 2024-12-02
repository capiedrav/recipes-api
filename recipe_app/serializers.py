"""
Serializers for recipe APIs
"""

from rest_framework import serializers
from core_app.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """

    class Meta:

        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id", ]


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe model.
    """

    tags = TagSerializer(many=True, required=False) # new field

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id", ]

    def _get_or_create_tags(self, tags, recipe):
        """
        Gets or creates tags as needed.
        """

        for tag in tags: # create or retrieve the tags from the database
            tag_obj, created = Tag.objects.get_or_create(user=self.context["request"].user, **tag)
            recipe.tags.add(tag_obj) # add the tags to the recipe

    def create(self, validated_data):
        """
        Create a recipe.
        """

        tags = validated_data.pop("tags", []) # remove tags from validate_data dict  
        recipe = Recipe.objects.create(**validated_data) # create the recipe
        self._get_or_create_tags(tags=tags, recipe=recipe)
        
        return recipe

    def update(self, instance, validated_data):
        """
        Update a recipe.
        """

        tags = validated_data.pop("tags", None) # remove tags from validate_data dict  

        if tags is not None: # add the new tags to the recipe
            instance.tags.clear() # clear existing recipe tags
            self._get_or_create_tags(tags=tags, recipe=instance)

        # update remaining fields of the recipe
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for recipe detail view.
    """

    class Meta(RecipeSerializer.Meta):

        fields = RecipeSerializer.Meta.fields + ["description", ]

