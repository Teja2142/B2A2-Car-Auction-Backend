from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utils.swagger import safe_generate_form_parameters, generate_form_parameters
from .serializers import RegisterSerializer, LoginSerializer, AdminUserCreateSerializer
from .models import User
import logging, uuid, requests, os
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .jwt_serializers import EmailTokenObtainPairSerializer
from .jwt_email_token import UserEmailTokenObtainSerializer
from .serializers import UserProfileUpdateSerializer, PartialUserProfileUpdateSerializer



@swagger_auto_schema(
    method='post',
    operation_description="User login with email & password.",
    operation_summary="User Login",
    manual_parameters=safe_generate_form_parameters(LoginSerializer),
    request_body=None,
    consumes=['application/x-www-form-urlencoded', 'multipart/form-data'],
    tags=['users']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    # Use filter rather than get to avoid MultipleObjectsReturned if legacy duplicates exist
    users_qs = User.objects.filter(email=email)
    if not users_qs.exists():
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    user = users_qs.order_by('-date_joined').first()
    if not user.check_password(password):
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    from .jwt_serializers import EmailTokenObtainPairSerializer
    refresh = EmailTokenObtainPairSerializer.get_token(user)
    return Response({
        'message': 'Login successful',
        'user': {
            'id': str(user.id),
            'email': user.email,
            'user_type': user.user_type
        },
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    })

@swagger_auto_schema(
    method='post',
    operation_description="Register a new user (customer or dealer).",
    operation_summary="User Registration",
    manual_parameters=safe_generate_form_parameters(RegisterSerializer),
    request_body=None,
    consumes=['application/x-www-form-urlencoded', 'multipart/form-data'],
    responses={201: openapi.Response(description='Registration successful'), 400: 'Validation error'},
    tags=['users']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def register_user(request):
    """
    Unified registration endpoint for both customers and dealers.
    """
    # Use ModelSerializer for handling file uploads
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Use the serializer to create the user
        user = serializer.save()
        
        # Generate the full name for response
        full_name = f"{user.first_name} {user.last_name}".strip()
        
        # Return success response with user details
        return Response({
            "message": f"{user.get_user_type_display()} registration successful!",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "user_type": user.user_type,
                "full_name": full_name
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        # Log the error for debugging
        logger = logging.getLogger(__name__)
        logger.error(f"Registration failed: {str(e)}")
        
        # Return error response
        return Response({
            "message": "Registration failed",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

# Password Reset Request - PUBLIC
@swagger_auto_schema(
    method='post',
    operation_description="Request password reset by providing your email address. You will receive a reset link.",
    operation_summary="Password Reset Request Form",
    manual_parameters=[
        openapi.Parameter(
            'email', openapi.IN_FORM, required=True, type=openapi.TYPE_STRING,
            description='Enter your registered email address', format='email',
            examples={'example': 'user@example.com'}
        )
    ],
    request_body=None,
    consumes=['application/x-www-form-urlencoded','multipart/form-data'],
    tags=['users']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def request_password_reset(request):
    """
    Request a password reset link.
    Sends an email with password reset instructions if the email exists in the system.
    """
    email = request.data.get('email')
    if not email:
        return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"message": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)

    # Generate and save a unique token
    reset_token = uuid.uuid4()
    user.reset_token = reset_token
    user.save()

    # Build the password reset link using backend URL
    reset_link = request.build_absolute_uri(f"/api/users/password-reset/{reset_token}/")
    print("reset_link:", reset_link)

    # Send the password reset email
    subject = "Password Reset Request"
    message = f"Click the link below to reset your password:\n{reset_link}"
    from_email = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        message,
        from_email,
        [email],
        fail_silently=False,
    )

    # (Optional) Also send via Mailgun if needed
    try:
        send_reset_pswd_link_message(reset_link, user)
    except Exception as e:
        # Use logging instead of print for error reporting
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Unable to send password reset mail from mailgun to the user: {e}')

    return Response({"message": "Password reset link sent to email."}, status=status.HTTP_200_OK)

# Password Reset Confirm - PUBLIC
@swagger_auto_schema(
    methods=['post'],
    manual_parameters=[
        openapi.Parameter('password', openapi.IN_FORM, required=True, type=openapi.TYPE_STRING, description='New password (must meet complexity requirements)'),
        openapi.Parameter('confirmPassword', openapi.IN_FORM, required=True, type=openapi.TYPE_STRING, description='Confirm new password')
    ],
    request_body=None,
    consumes=['application/x-www-form-urlencoded','multipart/form-data'],
    operation_description='Reset password using the token received via email.',
    tags=['users']
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def reset_password(request, token):
    """
    Handle password reset via token.
    GET: Render reset form (for web).
    POST: Reset password (for API or form).
    """
    try:
        user = User.objects.get(reset_token=token)
    except User.DoesNotExist:
        return Response({"message": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        return render(request, 'registration/password_reset_confirm.html', {"token": token})

    if request.method == 'POST':
        # Prefer request.data for API clients, fallback to POST for forms
        new_password = request.data.get("password") or request.POST.get("password")
        confirm_password = request.data.get("confirmPassword") or request.POST.get("confirmPassword")

        if not new_password or not confirm_password:
            return Response({"message": "Both password fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({"message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.reset_token = None
        user.save()

        # Redirect to homepage or show success message
        if request.accepts('text/html'):  # If the request is from a browser
            return render(request, 'registration/password_reset_success.html')
        else:  # For API clients
            return Response({"message": "Password reset successful!"}, status=status.HTTP_200_OK)




def send_reset_pswd_link_message(reset_link, user):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxf934aad3f3b64cd4a7a1311ffcdd545f.mailgun.org/messages",
        auth=("api", os.getenv('API_KEY', '0c887d2082c0cd158bf2a0892c23f52a-623424ea-31107b3f')),
        data={
            "from": "Mailgun Sandbox <postmaster@sandboxf934aad3f3b64cd4a7a1311ffcdd545f.mailgun.org>",
            "to": f"{user.username} <{user.email}>",
            "subject": f"Hello {user.username} Password Reset Request ",
            "text": f"""Hello {user.username}
                        Click the link below to reset your password:\n {reset_link}
            """})



# users/views.py



class CustomObtainAuthToken(ObtainAuthToken):
    # Explicitly allow unauthenticated access; global DEFAULT_PERMISSION_CLASSES enforces IsAuthenticated otherwise.
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Obtain JWT token by providing email and password.",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='Email address used to login', format='email'),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='User password', format='password')
        ],
        consumes=['application/x-www-form-urlencoded','multipart/form-data'],
        responses={200: openapi.Response('JWT token', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'token': openapi.Schema(type=openapi.TYPE_STRING)})), 400: 'Invalid email or password'},
        tags=['users']
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class SwaggerTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    # Ensure this remains publicly accessible for login
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Obtain JWT access and refresh tokens.",
        tags=['users'],
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='Email address', format='email'),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='Password', format='password')
        ],
        consumes=['application/x-www-form-urlencoded','multipart/form-data'],
        responses={200: openapi.Response('JWT token pair', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'access': openapi.Schema(type=openapi.TYPE_STRING), 'refresh': openapi.Schema(type=openapi.TYPE_STRING), 'user': openapi.Schema(type=openapi.TYPE_OBJECT)})), 401: 'Unauthorized'},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class SwaggerTokenRefreshView(TokenRefreshView):
    # Refresh requires only a valid refresh token, not existing session auth
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Refresh JWT access token.",
        tags=['users'],
        manual_parameters=[
            openapi.Parameter('refresh', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description='Refresh token')
        ],
        consumes=['application/x-www-form-urlencoded','multipart/form-data'],
        responses={200: openapi.Response('JWT access token', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'access': openapi.Schema(type=openapi.TYPE_STRING)})), 401: 'Unauthorized'},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserEmailTokenObtainView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Obtain JWT access and refresh tokens using email and password.",
        tags=['users'],
        manual_parameters=safe_generate_form_parameters(UserEmailTokenObtainSerializer),
        consumes=['application/x-www-form-urlencoded','multipart/form-data'],
        responses={200: openapi.Response('JWT token pair', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            'user': openapi.Schema(type=openapi.TYPE_OBJECT)
        })), 400: 'Invalid email or password'},
    )
    def post(self, request, *args, **kwargs):
        serializer = UserEmailTokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)

# ---------------------------
# User CRUD ViewSet (Admin)
# ---------------------------
from rest_framework import viewsets, permissions
from .serializers import UserSerializer, UserProfileUpdateSerializer, PartialUserProfileUpdateSerializer

class UserViewSet(viewsets.ModelViewSet):
    """Admin CRUD operations for users exposed with form-friendly Swagger parameters.

    Uses different serializers for create (registration), update (profile update) and read (standard user).
    Only admin users can access these endpoints by default.
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer
    lookup_field = 'id'
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        from .serializers import RegisterSerializer, AdminUserCreateSerializer  # local import to avoid circular issues
        if self.action == 'create':
            # Use admin serializer that can set staff/superuser flags
            return AdminUserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserSerializer

    @swagger_auto_schema(operation_summary="List Users", tags=['users'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create User (Admin)",
        tags=['users'],
        request_body=AdminUserCreateSerializer,
        responses={201: UserSerializer},
        consumes=['multipart/form-data']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Retrieve User", tags=['users'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update User (Full)",
        tags=['users'],
        request_body=UserProfileUpdateSerializer,
        responses={200: UserProfileUpdateSerializer},
        consumes=['multipart/form-data']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial Update User",
        tags=['users'],
        request_body=PartialUserProfileUpdateSerializer,
        responses={200: UserProfileUpdateSerializer},
        consumes=['multipart/form-data']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete User", tags=['users'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)




# --- Self-Service Profile Endpoint ---
class UserProfileView(APIView):
    """
    Allows an authenticated user (dealer or customer) to view and update their own profile.
    GET: Retrieve your profile.
    PUT/PATCH: Update your profile fields (no admin needed).
    """
    permission_classes = [IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(responses={200: UserProfileUpdateSerializer}, operation_summary="Get your profile", tags=["users"])
    def get(self, request):
        serializer = UserProfileUpdateSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserProfileUpdateSerializer,
        responses={200: UserProfileUpdateSerializer},
        operation_summary="Update your profile (full)",
        tags=["users"],
        consumes=['multipart/form-data']
    )
    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=PartialUserProfileUpdateSerializer,
        responses={200: UserProfileUpdateSerializer},
        operation_summary="Update your profile (partial)",
        tags=["users"],
        consumes=['multipart/form-data']
    )
    def patch(self, request):
        serializer = PartialUserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)