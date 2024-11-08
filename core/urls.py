from django.contrib import admin
from django.urls import path
from strawberry.django.views import GraphQLView
from api.schema import schema
from django.views.decorators.csrf import csrf_exempt

# apps/authentication/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt import views as jwt_views
from django.core.exceptions import PermissionDenied

# api/views.py


class AuthenticatedGraphQLViewMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, jwt_authenticator=None, *args, **kwargs):
        self.jwt_authenticator = jwt_authenticator or JWTAuthentication()
        super().__init__(*args, **kwargs)

    def get_context(self, request, response):
        """
        Override get_context to check if user is authenticated
        """
        try:
            # Perform authentication here - overriding get context so that graphql queries cant be executed without it
            auth_result = self.jwt_authenticator.authenticate(request)
            if auth_result is None:
                raise PermissionDenied("Authentication required")

            user, _ = auth_result
            request.user = user
            context = super().get_context(request, response)
            return context
        except Exception as e:
            raise PermissionDenied(f"Authentication required - {str(e)}")


class AuthenticatedGraphQLView(AuthenticatedGraphQLViewMixin, GraphQLView):
    pass


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/token/",
        csrf_exempt(jwt_views.TokenObtainPairView.as_view()),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        csrf_exempt(jwt_views.TokenRefreshView.as_view()),
        name="token_refresh",
    ),
    path("graphql/", csrf_exempt(AuthenticatedGraphQLView.as_view(schema=schema))),
]
