from typing import Optional, List
import strawberry
from strawberry.types import Info

from .models import Recipe
from .types import RecipeType


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
