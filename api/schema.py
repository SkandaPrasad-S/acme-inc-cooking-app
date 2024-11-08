import strawberry
from apps.ingredients.queries import Query as IngredientQuery
from apps.ingredients.mutations import Mutation as IngredientMutation
from apps.recipes.queries import Query as RecipeQuery
from apps.recipes.mutations import Mutation as RecipeMutation
from strawberry.types import Info


@strawberry.type
class Query(IngredientQuery, RecipeQuery):  # Combine IngredientQuery and RecipeQuery
    pass


@strawberry.type
class Mutation(
    IngredientMutation, RecipeMutation
):  # Combine IngredientMutation and RecipeMutation
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
