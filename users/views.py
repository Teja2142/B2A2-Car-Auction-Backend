from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import User
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

@api_view(['GET'])
def home(request):
    return render(request, 'index.html')

# ✅ Register User
@api_view(['POST'])
def register_user(request):
    name = request.data.get('name')
    mobile = request.data.get('mobile')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirmPassword')

    if not name or not mobile or not email or not password:
        return JsonResponse({"message": "All fields are required"}, status=400)

    if password != confirm_password:
        return JsonResponse({"message": "Passwords do not match"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"message": "Email already registered"}, status=400)

    user = User(name=name, mobile=mobile, email=email, password=make_password(password))
    user.save()
    
    return JsonResponse({"message": "Registration successful!"}, status=201)

# ✅ Login User
@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return JsonResponse({"message": "Email and password are required"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"message": "Invalid email or password"}, status=400)

    if not check_password(password, user.password):
        return JsonResponse({"message": "Invalid email or password"}, status=400)

    return JsonResponse({"message": "Login successful", "user": {"name": user.name, "email": user.email}}, status=200)

# ✅ Generate Password Reset Token
@api_view(['POST'])
def request_password_reset(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"message": "Email not found"}, status=400)

    # Generate and save a unique token
    reset_token = uuid.uuid4()
    user.reset_token = reset_token
    user.save()

    # Build the password reset link
    reset_link = f"http://127.0.0.1:8000/api/password-reset/{reset_token}/"

    # Send the password reset email
    subject = "Password Reset Request"
    message = f"Click the link below to reset your password:\n{reset_link}"
    from_email = settings.EMAIL_HOST_USER  # Sender's email (configured in environment variables)

    print("from_email:",from_email)
    print("to_email:",email)

    send_mail(
        subject,           # Subject line
        message,           # Message body
        from_email,        # From email
        [email],           # Recipient list
        fail_silently=False,  # If the email fails, Django will raise an exception
    )

    return JsonResponse({"message": "Password reset link sent to email."}, status=200)


# ✅ Reset Password
@api_view(['POST'])
def reset_password(request, token):
    try:
        user = User.objects.get(reset_token=token)
    except User.DoesNotExist:
        return JsonResponse({"message": "Invalid or expired token"}, status=400)

    new_password = request.data.get("password")
    confirm_password = request.data.get("confirmPassword")

    if not new_password or new_password != confirm_password:
        return JsonResponse({"message": "Passwords do not match"}, status=400)

    # Update password
    user.password = make_password(new_password)
    user.reset_token = None  # Invalidate token
    user.save()

    return JsonResponse({"message": "Password reset successful!"}, status=200)
