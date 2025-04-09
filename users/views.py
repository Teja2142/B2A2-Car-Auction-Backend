from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import User
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
import os
import requests

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()



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

    pswd_reset_base_url = settings.PSWD_RESET_BASE_LINK

    # Build the password reset link
    reset_link = f"{pswd_reset_base_url}/{reset_token}"
    try:
        send_reset_pswd_link_message(reset_link, user)
    except:
        print(f'unable to send pswd rest mail from mailgun to the user')

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




# ✅ Password Reset Form - GET Request
@api_view(['GET', 'POST'])
def reset_password(request, token):
    try:
        user = User.objects.get(reset_token=token)
    except User.DoesNotExist:
        return JsonResponse({"message": "Invalid or expired token"}, status=400)

    if request.method == 'GET':
        # Render the password reset form
        return render(request, 'registration/password_reset_confirm.html', {"token": token})

    if request.method == 'POST':
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        if not new_password or new_password != confirm_password:
            return JsonResponse({"message": "Passwords do not match"}, status=400)

        # Update password
        user.password = make_password(new_password)
        user.reset_token = None  # Invalidate token
        user.save()

        return JsonResponse({"message": "Password reset successful!"}, status=200)






def send_reset_pswd_link_message(reset_link,user):
  	return requests.post(
  		"https://api.mailgun.net/v3/sandboxf934aad3f3b64cd4a7a1311ffcdd545f.mailgun.org/messages",
  		auth=("api", os.getenv('API_KEY', '0c887d2082c0cd158bf2a0892c23f52a-623424ea-31107b3f')),
  		data={"from": "Mailgun Sandbox <postmaster@sandboxf934aad3f3b64cd4a7a1311ffcdd545f.mailgun.org>",
			"to": f"{user.name} <{user.email}>",
  			"subject": f"Hello {user.name} Password Reset Request ",
  			"text": f"""Hello {user.name}
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
