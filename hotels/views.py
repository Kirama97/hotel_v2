from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.db.models import Avg, Count, Min, Max, Sum, Q

from .models import Hotel
from .serializers import HotelSerializer, HotelListSerializer


class HotelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

   
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ['nom', 'adresse', 'email_contact']
    ordering_fields = ['prix_par_nuit', 'created_at', 'nom']
    ordering        = ['-created_at']

    def get_queryset(self):
        queryset = Hotel.objects.select_related('created_by').all()

        ville = self.request.query_params.get('ville')
        if ville:
            queryset = queryset.filter(adresse__icontains=ville)

        return queryset

    def get_serializer_class(self):
        return HotelListSerializer if self.action == 'list' else HotelSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        hotel = self.get_object()
        if hotel.created_by != request.user:
            return Response(
                {'error': "Vous ne pouvez modifier que vos propres hôtels."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        hotel = self.get_object()
        if hotel.created_by != request.user:
            return Response(
                {'error': "Vous ne pouvez supprimer que vos propres hôtels."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'], url_path='toggle-disponibilite')
    def toggle_disponibilite(self, request, pk=None):
        hotel = self.get_object()
        if hotel.created_by != request.user:
            return Response({'error': "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)
        hotel.est_disponible = not hotel.est_disponible
        hotel.save(update_fields=['est_disponible'])
        return Response({'id': hotel.id, 'est_disponible': hotel.est_disponible})

    @action(detail=False, methods=['get'], url_path='statistiques')
    def statistiques(self, request):
        queryset = Hotel.objects.all()
        stats = queryset.aggregate(
            total_hotels=Count('id'),
            prix_moyen=Avg('prix_par_nuit'),
            prix_min=Min('prix_par_nuit'),
            prix_max=Max('prix_par_nuit'),
        )
        return Response(stats)