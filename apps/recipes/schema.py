from typing import Optional, List
import strawberry
from strawberry.types import Info
from strawberry import auto
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Recipe, RecipeIngredient
from apps.ingredients.models import Ingredient
from apps.ingredients.schema import IngredientType

@strawberry.type
class RecipeIngredientType:
    id: int
    quantity: float
    notes: str
    ingredient: IngredientType

@strawberry.django.type(Recipe)
class RecipeType:
    id: auto
    name: auto
    description: auto
    instructions: auto
    cooking_time: auto
    created_at: auto
    updated_at: auto
    
    @strawberry.field
    def ingredients(self) -> List[RecipeIngredientType]:
        return RecipeIngredient.objects.filter(recipe=self)
    
    @strawberry.field
    def ingredient_count(self) -> int:
        return self.ingredient_count

@strawberry.input
class RecipeIngredientInput:
    ingredient_id: int
    quantity: float
    notes: Optional[str] = ""

@strawberry.input
class RecipeInput:
    name: str
    description: str
    instructions: str
    cooking_time: int
    ingredients: List[RecipeIngredientInput]

@strawberry.type
class RecipeError:
    message: str
    code: str

@strawberry.type
class RecipeResponse:
    success: bool
    recipe: Optional[RecipeType] = None
    error: Optional[RecipeError] = None

@strawberry.type
class Query:
    @strawberry.field
    def recipe(self, info: Info, id: int) -> Optional[RecipeType]:
        try:
            return Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            return None

    @strawberry.field
    def recipes(
        self,
        info: Info,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> List[RecipeType]:
        queryset = Recipe.objects.all()
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        return list(queryset[((page - 1) * page_size):(page * page_size)])

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
                        error=RecipeError(message="Name cannot be empty", code="EMPTY_NAME")
                    )

                # Check for duplicate recipe name
                if Recipe.objects.filter(name__iexact=name).exists():
                    return RecipeResponse(
                        success=False,
                        error=RecipeError(
                            message=f"Recipe with name '{name}' already exists",
                            code="DUPLICATE_NAME"
                        )
                    )

                # Create recipe
                recipe = Recipe.objects.create(
                    name=name,
                    description=input.description.strip(),
                    instructions=input.instructions.strip(),
                    cooking_time=input.cooking_time
                )

                # Add ingredients
                for ingredient_input in input.ingredients:
                    try:
                        ingredient = Ingredient.objects.get(pk=ingredient_input.ingredient_id)
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient=ingredient,
                            quantity=ingredient_input.quantity,
                            notes=ingredient_input.notes.strip()
                        )
                    except Ingredient.DoesNotExist:
                        raise ValidationError(f"Ingredient with ID {ingredient_input.ingredient_id} not found")

                return RecipeResponse(success=True, recipe=recipe)

        except ValidationError as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="VALIDATION_ERROR")
            )
        except Exception as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )

    @strawberry.mutation
    def add_ingredient_to_recipe(
        self,
        info: Info,
        recipe_id: int,
        ingredient_id: int,
        quantity: float,
        notes: Optional[str] = ""
    ) -> RecipeResponse:
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            if RecipeIngredient.objects.filter(recipe=recipe, ingredient=ingredient).exists():
                return RecipeResponse(
                    success=False,
                    error=RecipeError(
                        message=f"Ingredient already exists in recipe",
                        code="DUPLICATE_INGREDIENT"
                    )
                )

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=quantity,
                notes=notes.strip()
            )

            return RecipeResponse(success=True, recipe=recipe)

        except (Recipe.DoesNotExist, Ingredient.DoesNotExist) as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="NOT_FOUND")
            )
        except Exception as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )

    @strawberry.mutation
    def remove_ingredient_from_recipe(
        self,
        info: Info,
        recipe_id: int,
        ingredient_id: int
    ) -> RecipeResponse:
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            recipe_ingredient = RecipeIngredient.objects.filter(
                recipe=recipe,
                ingredient=ingredient
            ).first()

            if not recipe_ingredient:
                return RecipeResponse(
                    success=False,
                    error=RecipeError(
                        message="Ingredient not found in recipe",
                        code="NOT_FOUND"
                    )
                )

            recipe_ingredient.delete()
            return RecipeResponse(success=True, recipe=recipe)

        except (Recipe.DoesNotExist, Ingredient.DoesNotExist) as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="NOT_FOUND")
            )
        except Exception as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )
        
    @strawberry.mutation
    def delete_recipe(self, info: Info, recipe_id: int) -> RecipeResponse:
        try:
            # Try to find the recipe by ID
            recipe = Recipe.objects.get(pk=recipe_id)

            # Delete the recipe (this will also delete the related RecipeIngredient entries due to cascade)
            recipe.delete()

            return RecipeResponse(success=True, recipe=None)

        except Recipe.DoesNotExist:
            return RecipeResponse(
                success=False,
                error=RecipeError(message="Recipe not found", code="NOT_FOUND")
            )
        except Exception as e:
            return RecipeResponse(
                success=False,
                error=RecipeError(message=str(e), code="INTERNAL_ERROR")
            )