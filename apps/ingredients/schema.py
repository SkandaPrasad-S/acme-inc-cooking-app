from typing import Optional, List
import strawberry
from strawberry.types import Info
from strawberry import auto
from strawberry.django import django_resolver
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from .models import Ingredient


@strawberry.django.type(Ingredient)
class IngredientType:
    id: auto
    name: auto
    description: auto
    unit: auto
    created_at: auto
    updated_at: auto


@strawberry.input
class IngredientInput:
    name: str
    description: str
    unit: str



@strawberry.type
class Query:
    @strawberry.field
    def ingredient(self, info: Info, id: int) -> Optional[IngredientType]:
        try:
            ingredient = Ingredient.objects.get(pk=id)
            return ingredient
        except ObjectDoesNotExist:
            return None  # You can also return a custom error message if needed

    @strawberry.field
    def ingredients(
        self,
        info: Info,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> List[IngredientType]:
        # Validate page and page_size
        if page <= 0:
            raise ValueError("Page number must be greater than 0.")
        if page_size <= 0:
            raise ValueError("Page size must be greater than 0.")

        queryset = Ingredient.objects.all()

        # Search functionality (case-insensitive)
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Pagination logic
        paginator = Paginator(queryset, page_size)
        
        
        # Check if the page number is within the valid range
        if page > paginator.num_pages:
            return []  # Return an empty list if the page number is out of range
        
        # Return the ingredients for the given page
        return list(paginator.get_page(page))


@strawberry.type
class IngredientError:
    message: str
    code: str


@strawberry.type
class IngredientResponse:
    success: bool
    ingredient: Optional[IngredientType] = None
    error: Optional[IngredientError] = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_ingredient(
        self, info: Info, input: IngredientInput
    ) -> IngredientResponse:
        # Clean and validate input data
        name = input.name.strip()
        description = input.description.strip()
        unit = input.unit.strip().lower()

        # Validate required fields
        if not name:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message="Name cannot be empty", code="EMPTY_NAME"
                ),
            )

        if not unit:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message="Unit cannot be empty", code="EMPTY_UNIT"
                ),
            )

        try:
            # Check for existing ingredient case-insensitive
            if Ingredient.objects.filter(name__iexact=name).exists():
                return IngredientResponse(
                    success=False,
                    error=IngredientError(
                        message=f"Ingredient with name '{name}' already exists",
                        code="DUPLICATE_NAME",
                    ),
                )

            # Create the ingredient
            ingredient = Ingredient(name=name, description=description, unit=unit)

            # Full clean to run model validations
            ingredient.full_clean()
            ingredient.save()

            return IngredientResponse(success=True, ingredient=ingredient)

        except ValidationError as e:
            # Handle model validation errors
            return IngredientResponse(
                success=False,
                error=IngredientError(message=str(e), code="VALIDATION_ERROR"),
            )

        except IntegrityError as e:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message=f"Database integrity error occurred {str(e)}", code="INTEGRITY_ERROR"
                ),
            )

        except Exception as e:
            # Log unexpected errors here (you should add proper logging)
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message=f"An unexpected error occurred {str(e)}", code="INTERNAL_ERROR"
                ),
            )

    # Similarly, update other mutations to use the same pattern
    @strawberry.mutation
    def update_ingredient(
        self, info: Info, id: int, input: IngredientInput
    ) -> IngredientResponse:
        try:
            ingredient = Ingredient.objects.get(pk=id)

            # Clean and validate input data
            name = input.name.strip()
            description = input.description.strip()
            unit = input.unit.strip().lower()

            # Validate required fields
            if not name:
                return IngredientResponse(
                    success=False,
                    error=IngredientError(
                        message="Name cannot be empty", code="EMPTY_NAME"
                    ),
                )

            # Check if new name conflicts with existing ingredient (excluding current)
            if Ingredient.objects.filter(name__iexact=name).exclude(pk=id).exists():
                return IngredientResponse(
                    success=False,
                    error=IngredientError(
                        message=f"Another ingredient with name '{name}' already exists",
                        code="DUPLICATE_NAME",
                    ),
                )

            # Update fields
            ingredient.name = name
            ingredient.description = description
            ingredient.unit = unit

            # Validate and save
            ingredient.full_clean()
            ingredient.save()

            return IngredientResponse(success=True, ingredient=ingredient)

        except Ingredient.DoesNotExist:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message=f"Ingredient with ID {id} not found", code="NOT_FOUND"
                ),
            )
        except (ValidationError, IntegrityError) as e:
            return IngredientResponse(
                success=False,
                error=IngredientError(message=str(e), code="VALIDATION_ERROR"),
            )
        except Exception as e:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message=f"An unexpected error occurred {str(e)}",
                    code="INTERNAL_ERROR",
                ),
            )

    @strawberry.mutation
    def delete_ingredient(self, info: Info, id: int) -> IngredientResponse:
        try:
            ingredient = Ingredient.objects.get(pk=id)

            # Store ingredient data before deletion for response
            deleted_ingredient = ingredient

            # Perform deletion
            ingredient.delete()

            return IngredientResponse(
                success=True,
                ingredient=deleted_ingredient,  # Return the deleted ingredient data
            )

        except Ingredient.DoesNotExist:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message=f"Ingredient with ID {id} not found", code="NOT_FOUND"
                ),
            )
        except Exception as e:
            return IngredientResponse(
                success=False,
                error=IngredientError(
                    message=f"An unexpected error occurred during deletion {str(e)}",
                    code="DELETION_ERROR",
                ),
            )
