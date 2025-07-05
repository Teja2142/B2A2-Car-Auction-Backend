from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import DealerProfile
from .serializers import DealerProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .jwt_serializers import DealerEmailTokenObtainPairSerializer
from .jwt_email_token import DealerEmailTokenObtainSerializer
from rest_framework.views import APIView

class DealerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = DealerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company_name', 'city', 'state', 'country']
    search_fields = ['company_name', 'user__email', 'user__username']
    ordering_fields = ['company_name', 'created_at']
    ordering = ['company_name']
    lookup_field = "id"

    @swagger_auto_schema(
        tags=['dealers'],
        operation_description="List all dealer profiles. Supports search, ordering, and filtering.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by company name, user email, or username.", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by company_name or created_at. Example: ordering=-created_at", type=openapi.TYPE_STRING),
            openapi.Parameter('company_name', openapi.IN_QUERY, description="Filter by company name.", type=openapi.TYPE_STRING),
            openapi.Parameter('city', openapi.IN_QUERY, description="Filter by city.", type=openapi.TYPE_STRING),
            openapi.Parameter('state', openapi.IN_QUERY, description="Filter by state.", type=openapi.TYPE_STRING),
            openapi.Parameter('country', openapi.IN_QUERY, description="Filter by country.", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        # Only show the requesting user's profile in list
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'id') and user.id:
            queryset = DealerProfile.objects.filter(user=user)
        else:
            queryset = DealerProfile.objects.none()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['dealers'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['dealers'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['dealers'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['dealers'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['dealers'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        # Allow all DealerProfiles for permission checks, but filter in list
        return DealerProfile.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        obj = super().get_object()
        # Only allow the owner (dealer) to update/delete their own profile
        if self.request.user != obj.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have permission to modify this profile.')
        return obj

class DealerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Example: dealer123")
    email = serializers.EmailField(help_text="Example: dealer@example.com")
    password = serializers.CharField(write_only=True, help_text="Example: testpass123")
    company_name = serializers.CharField(help_text="Example: Sunrise Auto Group")
    address = serializers.CharField(help_text="Example: 123 Main St, Downtown")
    city = serializers.CharField(help_text="Example: Hyderabad")
    state = serializers.CharField(help_text="Example: Telangana")
    country = serializers.CharField(help_text="Example: India")
    phone = serializers.CharField(help_text="Example: +91-9876543210")
    website = serializers.URLField(required=False, allow_blank=True, help_text="Example: https://www.sunriseauto.com")

@swagger_auto_schema(
    method='post',
    request_body=DealerRegisterSerializer,
    # operation_description="Register a new dealer. Example payload: {\n  'username': 'dealer123',\n  'email': 'dealer@example.com',\n  'password': 'testpass123',\n  'company_name': 'Sunrise Auto Group',\n  'address': '123 Main St, Downtown',\n  'city': 'Hyderabad',\n  'state': 'Telangana',\n  'country': 'India',\n  'phone': '+91-9876543210',\n  'website': 'https://www.sunriseauto.com'\n}",
    tags=['dealers']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def dealer_register(request):
    serializer = DealerRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    User = get_user_model()
    if User.objects.filter(email=serializer.validated_data['email']).exists():
        return Response({'message': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(
        username=serializer.validated_data['username'],
        email=serializer.validated_data['email'],
        password=serializer.validated_data['password']
    )
    DealerProfile.objects.create(
        user=user,
        company_name=serializer.validated_data['company_name'],
        address=serializer.validated_data['address'],
        city=serializer.validated_data['city'],
        state=serializer.validated_data['state'],
        country=serializer.validated_data['country'],
        phone=serializer.validated_data['phone'],
        email=serializer.validated_data['email'],
        website=serializer.validated_data.get('website', ''),
        is_approved=False
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Dealer registered successfully!',
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }, status=status.HTTP_201_CREATED)

class DealerTokenObtainPairView(TokenObtainPairView):
    serializer_class = DealerEmailTokenObtainPairSerializer
    @swagger_auto_schema(
        operation_description="Obtain JWT access and refresh tokens for dealers.",
        tags=['dealers'],
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

class DealerEmailTokenObtainView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Obtain JWT access and refresh tokens for dealers using email and password.",
        tags=['dealers'],
        request_body=DealerEmailTokenObtainSerializer,
        responses={200: openapi.Response('JWT token pair', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            'user': openapi.Schema(type=openapi.TYPE_OBJECT)
        })), 400: 'Invalid email or password'},
    )
    def post(self, request, *args, **kwargs):
        serializer = DealerEmailTokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)
