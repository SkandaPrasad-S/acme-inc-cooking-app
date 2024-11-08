from typing import Optional, List
import strawberry
from strawberry.types import Info
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Recipe, RecipeIngredient
from apps.ingredients.models import Ingredient
from .inputs import RecipeInput, BulkUpdateRecipeIngredientInput
from .responses import RecipeResponse, RecipeError


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_recipe(self, info: Info, input: RecipeInput) -> RecipeResponse:
        try:
            with transaction.atomic():
                # Validate name
                name = input.name.strip()
                if not name:
                    return RecipeResponse(
                        success=False,
                        error=RecipeError(
                            message="Name cannot be empty", code="EMPTY_NAME"
                        ),
                    )

                # Check for duplicate recipe name
                if Recipe.objects.filter(name__iexact=name).exists():
                    return RecipeResponse(
                        success=False,
                        error=RecipeError(
                            message=f"Recipe with name '{name}' already exists",
                            code="DUPLICATE_NAME",
                        ),
                    )

                # Create recipe
                recipe = Recipe.objects.create(
                    name=name,
                    description=input.description.strip(),
                    instructions=input.instructions.strip(),
                    cooking_time=input.cooking_time,
                )

                # Add ingredients
                for ingredient_input in input.ingredients:
                    try:
                        ingredient = Ingredient.objects.get(
                            pk=ingredient_input.ingredient_id
                        )
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient=ingredient,
                            quantity=ingredient_input.quantity,
                            notes=ingredient_input.notes.strip(),
                        )
                    except Ingredient.DoesNotExist:
                        raise ValidationError(
                            f"Ingredient with ID {ingredient_input.ingredient_id} not found"
                        )

                return RecipeResponse(success=True, recipe=recipe)

        except ValidationError as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="VALIDATION_ERROR"),
            )
        except Exception as e:
            return RecipeResponse(
                success=False, error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )

    @strawberry.mutation
    def add_one_ingredient_to_recipe(
        self,
        info: Info,
        recipe_id: int,
        ingredient_id: int,
        quantity: float,
        notes: Optional[str] = "",
    ) -> RecipeResponse:
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            if RecipeIngredient.objects.filter(
                recipe=recipe, ingredient=ingredient
            ).exists():
                return RecipeResponse(
                    success=False,
                    error=RecipeError(
                        message="Ingredient already exists in recipe",
                        code="DUPLICATE_INGREDIENT",
                    ),
                )

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=quantity,
                notes=notes.strip(),
            )

            return RecipeResponse(success=True, recipe=recipe)

        except (Recipe.DoesNotExist, Ingredient.DoesNotExist) as e:
            return RecipeResponse(
                success=False, error=RecipeError(message=str(e), code="NOT_FOUND")
            )
        except Exception as e:
            return RecipeResponse(
                success=False, error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )

    @strawberry.mutation
    def remove_one_ingredient_from_recipe(
        self, info: Info, recipe_id: int, ingredient_id: int
    ) -> RecipeResponse:
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            recipe_ingredient = RecipeIngredient.objects.filter(
                recipe=recipe, ingredient=ingredient
            ).first()

            if not recipe_ingredient:
                return RecipeResponse(
                    success=False,
                    error=RecipeError(
                        message="Ingredient not found in recipe", code="NOT_FOUND"
                    ),
                )

            recipe_ingredient.delete()
            return RecipeResponse(success=True, recipe=recipe)

        except (Recipe.DoesNotExist, Ingredient.DoesNotExist) as e:
            return RecipeResponse(
                success=False, error=RecipeError(message=str(e), code="NOT_FOUND")
            )
        except Exception as e:
            return RecipeResponse(
                success=False, error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )

    @strawberry.mutation
    def delete_recipe(self, info: Info, recipe_id: int) -> RecipeResponse:
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe.delete()

            return RecipeResponse(success=True, recipe=None)

        except Recipe.DoesNotExist:
            return RecipeResponse(
                success=False,
                error=RecipeError(message="Recipe not found", code="NOT_FOUND"),
            )
        except Exception as e:
            return RecipeResponse(
                success=False, error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )

    @strawberry.mutation
    def bulk_update_recipe_ingredients(
        self,
        info: Info,
        recipe_id: int,
        ingredients: List[BulkUpdateRecipeIngredientInput]
    ) -> RecipeResponse:
        try:
            recipe = Recipe.objects.get(pk=recipe_id)

            for ingredient_data in ingredients:
                ingredient = Ingredient.objects.get(pk=ingredient_data.ingredient_id)

                # Check if the ingredient exists in the recipe, then update or create it
                recipe_ingredient, created = RecipeIngredient.objects.update_or_create(
                    recipe=recipe,
                    ingredient=ingredient,
                    defaults={
                        "quantity": ingredient_data.quantity,
                        "notes": ingredient_data.notes.strip()
                    }
                )

            return RecipeResponse(success=True, recipe=recipe)

        except Recipe.DoesNotExist:
            return RecipeResponse(
                success=False,
                error=RecipeError(message="Recipe not found", code="NOT_FOUND")
            )
        except Ingredient.DoesNotExist as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="NOT_FOUND")
            )
        except Exception as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )