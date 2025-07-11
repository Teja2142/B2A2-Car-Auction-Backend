from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import User
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
import os
import requests
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegisterSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
import logging

logging.basicConfig(level=logging.INFO)



@swagger_auto_schema(method='post', request_body=LoginSerializer, responses={200: 'Login successful', 400: 'Invalid email or password'})
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    User login endpoint. Accepts email and password, returns token and user info on success.
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

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        "message": "Login successful",
        "user": {"id": str(user.id), "username": user.username, "email": user.email},
        "token": token.key
    }, status=status.HTTP_200_OK)



@swagger_auto_schema(method='post', request_body=RegisterSerializer, responses={201: 'Registration successful', 400: 'Validation error'})
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    User registration endpoint. Accepts name, mobile, email, password, confirmPassword. Returns success message on registration.
    """
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    name = serializer.validated_data['name']
    mobile = serializer.validated_data['mobile']
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    confirm_password = serializer.validated_data['confirmPassword']

    if password != confirm_password:
        return Response({"message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"message": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(mobile=mobile).exists():
        return Response({"message": "Mobile already registered"}, status=status.HTTP_400_BAD_REQUEST)

    user = User(username=name, mobile=mobile, email=email)
    user.set_password(password)
    user.save()
    return Response({"message": "Registration successful!", "user": {"id": str(user.id), "username": user.username, "email": user.email}}, status=status.HTTP_201_CREATED)

# Password Reset Request - PUBLIC
@swagger_auto_schema(method='post', request_body=PasswordResetRequestSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
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
@swagger_auto_schema(method='post', request_body=PasswordResetConfirmSerializer)
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
