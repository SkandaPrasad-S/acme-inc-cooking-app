
---

# Ingredient Management API

This API enables management of ingredients with features like ingredient creation, retrieval, updating, deletion, pagination, and search. Built using Django, Django Rest Framework, and Strawberry GraphQL, the API is equipped to handle essential CRUD operations with validations and error handling.

## Setup

Ensure you have set up your Django and Strawberry GraphQL environment. This project requires:

- Django
- Strawberry GraphQL
- Django Rest Framework (for optional REST integration)
- PostgreSQL or SQLite (for development)

After setting up your environment, apply migrations to create database tables for your models:
```bash
python manage.py migrate
```

To create a superuser for testing:
```bash
python manage.py createsuperuser
```

To run the server:
```bash
python manage.py runserver
```

You can now access the GraphQL interface at `http://localhost:8000/graphql`.

## API Queries and Mutations

Use the following GraphQL queries and mutations to test the Ingredient Management API. These include sample values for testing.

Way to get a token and use the api end points

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"notuser\", \"password\": \"notmypassword\"}" http://127.0.0.1:8000/api/token/ #first way

curl -X POST -d "username=<username>&password=<password>" http://127.0.0.1:8000/auth/token/ #second way


curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <your-access-token>" -d "{\"query\":\"query { ingredient(id: 1) { id, name, description, unit } }\"}" http://127.0.0.1:8000/graphql/
```

### Queries

#### 1. Get an Ingredient by ID
Retrieve details of a specific ingredient using its ID.
```graphql
query {
  ingredient(id: 1) {
    id
    name
    description
    unit
    createdAt
    updatedAt
  }
}
```

#### 2. List Ingredients with Pagination and Search
Retrieve a paginated list of ingredients, with optional search functionality.
```graphql
query {
  ingredients(page: 1, pageSize: 10, search: "sugar") {
    id
    name
    description
    unit
  }
}
```

### Mutations

#### 1. Create an Ingredient
Create a new ingredient by providing its name, description, and unit.
```graphql
mutation {
  createIngredient(input: { name: "Sugar", description: "Sweetening agent", unit: "grams" }) {
    success
    ingredient {
      id
      name
      description
      unit
    }
    error {
      message
      code
    }
  }
}
```

#### 2. Update an Ingredient
Update an existing ingredient by providing its ID and new values.
```graphql
mutation {
  updateIngredient(id: 1, input: { name: "Salt", description: "Used in seasoning", unit: "grams" }) {
    success
    ingredient {
      id
      name
      description
      unit
    }
    error {
      message
      code
    }
  }
}
```

#### 3. Delete an Ingredient
Delete an ingredient using its ID.
```graphql
mutation {
  deleteIngredient(id: 1) {
    success
    ingredient {
      id
      name
      description
      unit
    }
    error {
      message
      code
    }
  }
}
```

## Error Handling

Each mutation response includes an error field to handle cases where operations cannot be completed. The `error` object will include a message and a code detailing the issue, such as:

- `EMPTY_NAME`: When the name field is empty.
- `DUPLICATE_NAME`: When an ingredient with the same name already exists.
- `NOT_FOUND`: When an ingredient with the specified ID is not found.
- `INTEGRITY_ERROR`: When a database integrity issue occurs.

Here's a `README.md` to help you test all the available queries and mutations for your recipes in your Django/GraphQL project:

---

# Recipe Management GraphQL API

This API allows you to create, read, update, and delete recipes, as well as manage ingredients associated with each recipe. Below are examples of each query and mutation with sample values to help you get started.

## Table of Contents

1. [Queries](#queries)
   - [Get a Recipe by ID](#get-a-recipe-by-id)
   - [Get a List of Recipes with Pagination](#get-a-list-of-recipes-with-pagination)
2. [Mutations](#mutations)
   - [Create a Recipe](#create-a-recipe)
   - [Add Ingredient to a Recipe](#add-ingredient-to-a-recipe)
   - [Remove Ingredient from a Recipe](#remove-ingredient-from-a-recipe)
   - [Delete a Recipe](#delete-a-recipe)

---

## Queries

### Get a Recipe by ID

Retrieve a specific recipe by its ID.

#### Query

```graphql
query GetRecipe($id: Int!) {
  recipe(id: $id) {
    id
    name
    description
    instructions
    cookingTime
    ingredients {
      id
      quantity
      notes
      ingredient {
        id
        name
      }
    }
    ingredientCount
  }
}
```

#### Variables

```json
{
  "id": 1
}
```

---

### Get a List of Recipes with Pagination

Retrieve a paginated list of recipes, with optional search functionality.

#### Query

```graphql
query GetRecipes($page: Int!, $pageSize: Int!, $search: String) {
  recipes(page: $page, pageSize: $pageSize, search: $search) {
    id
    name
    description
    cookingTime
  }
}
```

#### Variables

```json
{
  "page": 1,
  "pageSize": 10,
  "search": "pasta"
}
```

---

## Mutations

### Create a Recipe

Create a new recipe with associated ingredients.

#### Mutation

```graphql
mutation CreateRecipe($input: RecipeInput!) {
  createRecipe(input: $input) {
    success
    recipe {
      id
      name
      description
      instructions
      cookingTime
      ingredients {
        id
        quantity
        notes
        ingredient {
          id
          name
        }
      }
    }
    error {
      message
      code
    }
  }
}
```

#### Variables

```json
{
  "input": {
    "name": "Spaghetti Bolognese",
    "description": "A classic Italian pasta dish.",
    "instructions": "Boil pasta, cook sauce, mix together.",
    "cookingTime": 30,
    "ingredients": [
      {
        "ingredientId": 1,
        "quantity": 200,
        "notes": "Use fresh tomatoes if possible"
      },
      {
        "ingredientId": 2,
        "quantity": 100,
        "notes": ""
      }
    ]
  }
}
```

---

### Add Ingredient to a Recipe

Add an additional ingredient to an existing recipe.

#### Mutation

```graphql
mutation AddIngredientToRecipe($recipeId: Int!, $ingredientId: Int!, $quantity: Float!, $notes: String) {
  addIngredientToRecipe(recipeId: $recipeId, ingredientId: $ingredientId, quantity: $quantity, notes: $notes) {
    success
    recipe {
      id
      name
      ingredients {
        id
        ingredient {
          id
          name
        }
        quantity
        notes
      }
    }
    error {
      message
      code
    }
  }
}
```

#### Variables

```json
{
  "recipeId": 1,
  "ingredientId": 3,
  "quantity": 50,
  "notes": "Add towards the end of cooking"
}
```

---

### Remove Ingredient from a Recipe

Remove an ingredient from an existing recipe.

#### Mutation

```graphql
mutation RemoveIngredientFromRecipe($recipeId: Int!, $ingredientId: Int!) {
  removeIngredientFromRecipe(recipeId: $recipeId, ingredientId: $ingredientId) {
    success
    recipe {
      id
      name
      ingredients {
        id
        ingredient {
          id
          name
        }
        quantity
      }
    }
    error {
      message
      code
    }
  }
}
```

#### Variables

```json
{
  "recipeId": 1,
  "ingredientId": 2
}
```

---

### Delete a Recipe

Delete a recipe by its ID.

#### Mutation

```graphql
mutation DeleteRecipe($recipeId: Int!) {
  deleteRecipe(recipeId: $recipeId) {
    success
    error {
      message
      code
    }
  }
}
```

#### Variables

```json
{
  "recipeId": 1
}
```

---

## Notes

- All recipes and ingredients are identified by unique IDs.
- For creating a recipe, you must pass at least one ingredient with its ID, quantity, and optional notes.
- The `ingredientCount` field in `RecipeType` automatically counts the ingredients associated with each recipe.



## License

This project is open-source under the MIT License. 

---

This file should help developers understand the project structure, setup, and usage, providing clear steps for testing each API endpoint.