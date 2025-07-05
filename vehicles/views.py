from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from .models import Vehicle, VehicleImage
from .serializers import VehicleSerializer, VehicleImageSerializer, MultipleVehicleImageUploadSerializer
from drf_yasg.utils import swagger_auto_schema
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

    @swagger_auto_schema(tags=['vehicles'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'dealer_profile'):
            serializer.save(dealer=self.request.user.dealer_profile)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'dealer_profile') and user.dealer_profile:
            return Vehicle.objects.filter(dealer=user.dealer_profile)
        return Vehicle.objects.all()

    def perform_update(self, serializer):
        # Only allow dealer to update their own vehicle
        if self.get_object().dealer == self.request.user.dealer_profile:
            serializer.save()
        else:
            raise PermissionDenied('You do not have permission to update this vehicle.')

    def perform_destroy(self, instance):
        # Only allow dealer to delete their own vehicle
        if instance.dealer == self.request.user.dealer_profile:
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

    @swagger_auto_schema(tags=['vehicles'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['vehicles'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='bulk-upload', serializer_class=MultipleVehicleImageUploadSerializer)
    @swagger_auto_schema(tags=['vehicles'], operation_description="Upload multiple images for a vehicle.")
    def bulk_upload(self, request):
        serializer = MultipleVehicleImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'images uploaded'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
