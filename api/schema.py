import strawberry
from apps.ingredients.schema import Query as IngredientQuery
from apps.ingredients.schema import Mutation as IngredientMutation
from apps.recipes.schema import Query as RecipeQuery
from apps.recipes.schema import Mutation as RecipeMutation

@strawberry.type
class Query(IngredientQuery, RecipeQuery):  # Combine IngredientQuery and RecipeQuery
    pass

@strawberry.type
class Mutation(IngredientMutation, RecipeMutation):  # Combine IngredientMutation and RecipeMutation
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)