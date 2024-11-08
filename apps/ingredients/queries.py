# graphql/queries.py
import strawberry
from typing import List, Optional
from strawberry.types import Info
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from .types import IngredientType
from .models import Ingredient


@strawberry.type
class Query:
    @strawberry.field
    def ingredient(self, info: Info, id: int) -> Optional[IngredientType]:
        try:
            return Ingredient.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None

    @strawberry.field
    def ingredients(
        self,
        info: Info,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> List[IngredientType]:
        if page <= 0 or page_size <= 0:
            raise ValueError("Page number and page size must be greater than 0.")

        queryset = Ingredient.objects.all()

        if search:
            queryset = queryset.filter(name__icontains=search)

        paginator = Paginator(queryset, page_size)
        return list(paginator.get_page(page)) if page <= paginator.num_pages else []
