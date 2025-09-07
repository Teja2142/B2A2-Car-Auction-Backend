from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import User
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer
)
from .jwt_serializers import EmailTokenObtainPairSerializer
from .jwt_email_token import UserEmailTokenObtainSerializer

import os
import uuid
import logging
import requests

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



@swagger_auto_schema(
    method='post', 
    request_body=LoginSerializer, 
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='JWT access token (valid for 15 minutes)'
                            ),
                            'refresh': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='JWT refresh token (valid for 24 hours)'
                            ),
                        }
                    ),
                }
            )
        ), 
        400: 'Invalid email or password'
    }, 
    tags=['users']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    User login endpoint. 
    Accepts email and password, returns:
    - User information
    - JWT access token (valid for 15 minutes)
    - JWT refresh token (valid for 24 hours)
    
    Use the access token in the Authorization header as:
    Authorization: Bearer <access_token>
    
    When the access token expires, use the refresh token to get a new one
    via the /api/users/jwt/refresh/ endpoint.
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"message": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({"message": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

    # Generate JWT tokens
    refresh = EmailTokenObtainPairSerializer.get_token(user)
    
    return Response({
        "message": "Login successful",
        "user": {
            "id": str(user.id), 
            "username": user.username, 
            "email": user.email,
            "user_type": user.user_type
        },
        "tokens": {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    }, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method='post',
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response(
            description='Registration successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        400: 'Validation error'
    },
    tags=['users']
)
@api_view(['POST'])
@permission_classes([AllowAny])
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
    request_body=PasswordResetRequestSerializer,
    responses={
        200: openapi.Response(
            description='Password reset link sent successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Success message'
                    )
                }
            )
        ),
        400: openapi.Response(
            description='Bad request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Error message'
                    )
                }
            )
        )
    },
    operation_description='Request a password reset link. An email will be sent with reset instructions.',
    tags=['users']
)
@api_view(['POST'])
@permission_classes([AllowAny])
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
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['password', 'confirmPassword'],
        properties={
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='New password (must meet complexity requirements)'
            ),
            'confirmPassword': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Confirm new password'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description='Password reset successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Success message'
                    )
                }
            )
        ),
        400: openapi.Response(
            description='Bad request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Error message'
                    )
                }
            )
        )
    },
    operation_description='Reset password using the token received via email.',
    tags=['users']
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
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
    @swagger_auto_schema(
        operation_description="Obtain JWT token by providing email and password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            },
        ),
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
    @swagger_auto_schema(
        operation_description="Obtain JWT access and refresh tokens.",
        tags=['users'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            },
        ),
        responses={200: openapi.Response('JWT token pair', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'access': openapi.Schema(type=openapi.TYPE_STRING), 'refresh': openapi.Schema(type=openapi.TYPE_STRING), 'user': openapi.Schema(type=openapi.TYPE_OBJECT)})), 401: 'Unauthorized'},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class SwaggerTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_description="Refresh JWT access token.",
        tags=['users'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: openapi.Response('JWT access token', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'access': openapi.Schema(type=openapi.TYPE_STRING)})), 401: 'Unauthorized'},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserEmailTokenObtainView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Obtain JWT access and refresh tokens using email and password.",
        tags=['users'],
        request_body=UserEmailTokenObtainSerializer,
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
