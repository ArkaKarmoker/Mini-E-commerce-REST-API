from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for registering a new user.
    On successful registration, returns user profile data and an auth token.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account and returns an authentication token.",
        responses={
            201: OpenApiResponse(description="User registered successfully"),
            400: OpenApiResponse(description="Validation error"),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response(
            {
                "message": "User registered successfully.",
                "token": token.key,
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    API endpoint for user login.
    Takes username and password and returns an auth token.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User Login",
        description="Authenticate with username and password to retrieve an authentication token.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "message": "Login successful.",
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    API endpoint for user logout.
    Deletes the token for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User Logout",
        description="Invalidates and deletes the current user's authentication token.",
        request=None,
        responses={
            200: OpenApiResponse(description="Logged out successfully"),
            401: OpenApiResponse(description="Unauthorized"),
        }
    )
    def post(self, request, *args, **kwargs):
        # Delete user token
        Token.objects.filter(user=request.user).delete()
        return Response(
            {"message": "Logged out successfully. Token invalidated."},
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating the authenticated user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get/Update User Profile",
        description="Returns or updates profile details of the currently authenticated user.",
    )
    def get_object(self):
        return self.request.user
