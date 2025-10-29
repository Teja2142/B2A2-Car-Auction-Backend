from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from .models import Vehicle, VehicleImage
from .serializers import (
    VehicleSerializer,
    VehicleImageSerializer,
    MultipleVehicleImageUploadSerializer,
    PartialVehicleSerializer,
    PartialVehicleImageSerializer
)
from drf_yasg.utils import swagger_auto_schema
from utils.swagger import safe_generate_form_parameters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['make', 'model', 'year', 'color', 'status', 'dealer']
    search_fields = ['vin', 'make', 'model', 'features', 'description', 'registration_number']
    ordering_fields = ['year', 'mileage', 'price', 'starting_price', 'created_at']
    ordering = ['-created_at']

    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="List all vehicles. Supports search, ordering, and filtering.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by VIN, make, model, features, description, or registration number.", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by year, mileage, price, starting_price, or created_at. Example: ordering=-created_at", type=openapi.TYPE_STRING),
            openapi.Parameter('make', openapi.IN_QUERY, description="Filter by make.", type=openapi.TYPE_STRING),
            openapi.Parameter('model', openapi.IN_QUERY, description="Filter by model.", type=openapi.TYPE_STRING),
            openapi.Parameter('year', openapi.IN_QUERY, description="Filter by year.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('color', openapi.IN_QUERY, description="Filter by color.", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status.", type=openapi.TYPE_STRING),
            openapi.Parameter('dealer', openapi.IN_QUERY, description="Filter by dealer ID.", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="Create vehicle.",
        operation_summary="Create Vehicle",
        # We provide manual form parameters; disable automatic body introspection to avoid
        # drf-yasg attempting to build a JSON schema containing File/Image fields.
        manual_parameters=safe_generate_form_parameters(VehicleSerializer),
        request_body=None,
        consumes=['application/x-www-form-urlencoded', 'multipart/form-data'],
        responses={201: openapi.Response('Created'), 400: 'Bad data'}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="Partial update vehicle.",
        operation_summary="Partial Update Vehicle",
        manual_parameters=safe_generate_form_parameters(PartialVehicleSerializer),
        request_body=None,
        consumes=['application/x-www-form-urlencoded', 'multipart/form-data'],
        responses={200: openapi.Response('Updated'), 400: 'Bad data', 403: 'Forbidden', 404: 'Not found'}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="Full update vehicle (all required fields must be provided).",
        operation_summary="Update Vehicle",
        manual_parameters=safe_generate_form_parameters(VehicleSerializer),
        request_body=None,
        consumes=['application/x-www-form-urlencoded', 'multipart/form-data'],
        responses={200: openapi.Response('Updated'), 400: 'Bad data', 403: 'Forbidden', 404: 'Not found'}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated and getattr(user, 'user_type', None) == 'dealer':
            serializer.save(dealer=user)
        else:
            # Non-dealers can create without dealer linkage (or raise if not allowed)
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, 'user_type', None) == 'dealer':
            return Vehicle.objects.filter(dealer=user)
        return Vehicle.objects.all()

    def perform_update(self, serializer):
        # Only dealer owner can update
        instance = self.get_object()
        if instance.dealer and instance.dealer == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied('You do not have permission to update this vehicle.')

    def perform_destroy(self, instance):
        # Only dealer owner can delete
        if instance.dealer and instance.dealer == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied('You do not have permission to delete this vehicle.')

class VehicleImageViewSet(viewsets.ModelViewSet):
    queryset = VehicleImage.objects.all()
    serializer_class = VehicleImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(tags=['vehicles'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="Create vehicle image (multipart form).",
        operation_summary="Create Vehicle Image",
        manual_parameters=safe_generate_form_parameters(VehicleImageSerializer),
        request_body=None,
        consumes=['multipart/form-data'],
        responses={201: openapi.Response('Created'), 400: 'Bad data'}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="Update vehicle image (replace file or change vehicle).",
        operation_summary="Update Vehicle Image",
        manual_parameters=safe_generate_form_parameters(VehicleImageSerializer),
        request_body=None,
        consumes=['multipart/form-data'],
        responses={200: openapi.Response('Updated'), 400: 'Bad data'}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="Partial update vehicle image (only send fields to change).",
        operation_summary="Partial Update Vehicle Image",
        manual_parameters=safe_generate_form_parameters(PartialVehicleImageSerializer),
        request_body=None,
        consumes=['multipart/form-data'],
        responses={200: openapi.Response('Updated'), 400: 'Bad data'}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # NOTE: We intentionally omit serializer_class here to prevent drf_yasg from auto-introspecting
    # the MultipleVehicleImageUploadSerializer (ListField of ImageField) which triggers a FileField
    # schema error. We supply manual_parameters + request_body=None in the swagger decorator instead.
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    @swagger_auto_schema(
        tags=['vehicles'],
        operation_description="Upload multiple images for a vehicle in one request.",
        operation_summary="Bulk Upload Vehicle Images",
        manual_parameters=safe_generate_form_parameters(MultipleVehicleImageUploadSerializer),
        request_body=None,
        consumes=['multipart/form-data'],
        responses={201: openapi.Response('Images Uploaded'), 400: 'Bad data'}
    )
    def bulk_upload(self, request):
        serializer = MultipleVehicleImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'images uploaded'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
