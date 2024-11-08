# graphql/mutations.py
import strawberry
from strawberry.types import Info
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Ingredient
from .inputs import IngredientInput
from .responses import IngredientResponse, IngredientError


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_ingredient(
        self, info: Info, input: IngredientInput
    ) -> IngredientResponse:
        name, description, unit = (
            input.name.strip(),
            input.description.strip(),
            input.unit.strip().lower(),
        )

        if not name or not unit:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message="Name and Unit cannot be empty", code="EMPTY_FIELD"
                ),
            )

        try:
            if Ingredient.objects.filter(name__iexact=name).exists():
                return IngredientResponse(
                    success=False,
                    error=IngredientError(
                        message="Duplicate ingredient name", code="DUPLICATE_NAME"
                    ),
                )

            ingredient = Ingredient(name=name, description=description, unit=unit)
            ingredient.full_clean()
            ingredient.save()
            return IngredientResponse(success=True, ingredient=ingredient)

        except (ValidationError, IntegrityError) as e:
            return IngredientResponse(
                success=False,
                error=IngredientError(message=str(e), code="DATABASE_ERROR"),
            )

    @strawberry.mutation
    def update_ingredient(
        self, info: Info, id: int, input: IngredientInput
    ) -> IngredientResponse:
        try:
            ingredient = Ingredient.objects.get(pk=id)
            name, description, unit = (
                input.name.strip(),
                input.description.strip(),
                input.unit.strip().lower(),
            )

            if not name:
                return IngredientResponse(
                    success=False,
                    error=IngredientError(
                        message="Name cannot be empty", code="EMPTY_NAME"
                    ),
                )

            if Ingredient.objects.filter(name__iexact=name).exclude(pk=id).exists():
                return IngredientResponse(
                    success=False,
                    error=IngredientError(
                        message="Duplicate ingredient name", code="DUPLICATE_NAME"
                    ),
                )

            ingredient.name, ingredient.description, ingredient.unit = (
                name,
                description,
                unit,
            )
            ingredient.full_clean()
            ingredient.save()
            return IngredientResponse(success=True, ingredient=ingredient)

        except Ingredient.DoesNotExist:
            return IngredientResponse(
                success=False,
                error=IngredientError(message="Ingredient not found", code="NOT_FOUND"),
            )

    @strawberry.mutation
    def delete_ingredient(self, info: Info, id: int) -> IngredientResponse:
        try:
            ingredient = Ingredient.objects.get(pk=id)
            ingredient.delete()
            return IngredientResponse(success=True, ingredient=ingredient)

        except Ingredient.DoesNotExist:
            return IngredientResponse(
                success=False,
                error=IngredientError(message="Ingredient not found", code="NOT_FOUND"),
            )
