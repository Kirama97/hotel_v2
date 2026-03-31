"""
hotels/views.py

Règles métier :
- Tout utilisateur connecté peut VOIR tous les hôtels (GET)
- Tout utilisateur connecté peut CRÉER un hôtel (POST)
- Seul le CRÉATEUR peut modifier ou supprimer son hôtel (PUT/PATCH/DELETE)
- En cas de tentative non autorisée → 403 Forbidden

Endpoints générés par le Router :
GET    /api/hotels/                             → liste de tous les hôtels
POST   /api/hotels/                             → créer un hôtel
GET    /api/hotels/{id}/                        → détail d'un hôtel
PUT    /api/hotels/{id}/                        → modifier (complet)
PATCH  /api/hotels/{id}/                        → modifier (partiel)
DELETE /api/hotels/{id}/                        → supprimer

Actions personnalisées :
PATCH  /api/hotels/{id}/toggle-disponibilite/   → basculer la disponibilité
GET    /api/hotels/statistiques/                → stats globales
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Min, Max, Sum, Q

from .models import Hotel
from .serializers import HotelSerializer, HotelListSerializer


class HotelViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['nom', 'ville', 'pays', 'description']
    ordering_fields    = ['prix_par_nuit', 'etoiles', 'created_at', 'nom', 'nombre_chambres']
    ordering           = ['-created_at']

    # ── Queryset : TOUS les hôtels, avec filtres optionnels ───────────────────

    def get_queryset(self):
        """
        Tous les hôtels de tous les utilisateurs.
        Filtres via query params :
          ?etoiles=4         → filtrer par nombre d'étoiles
          ?disponible=true   → filtrer par disponibilité
          ?ville=Dakar       → filtrer par ville (insensible à la casse)
          ?search=thies      → recherche texte (nom, ville, pays, description)
          ?ordering=-prix_par_nuit → tri
        """
        queryset = Hotel.objects.select_related('created_by').all()

        etoiles = self.request.query_params.get('etoiles')
        if etoiles:
            queryset = queryset.filter(etoiles=etoiles)

        disponible = self.request.query_params.get('disponible')
        if disponible is not None:
            queryset = queryset.filter(est_disponible=disponible.lower() == 'true')

        ville = self.request.query_params.get('ville')
        if ville:
            queryset = queryset.filter(ville__icontains=ville)

        return queryset

    def get_serializer_class(self):
        """Liste allégée, détail/création/modification complet."""
        return HotelListSerializer if self.action == 'list' else HotelSerializer

    # ── Création ──────────────────────────────────────────────────────────────

    def perform_create(self, serializer):
        """Associe automatiquement l'hôtel à l'utilisateur connecté."""
        serializer.save(created_by=self.request.user)

    # ── Modification — réservée au créateur ───────────────────────────────────

    def update(self, request, *args, **kwargs):
        hotel = self.get_object()
        if hotel.created_by != request.user:
            return Response(
                {'error': "Vous ne pouvez modifier que vos propres hôtels."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    # ── Suppression — réservée au créateur ───────────────────────────────────

    def destroy(self, request, *args, **kwargs):
        hotel = self.get_object()
        if hotel.created_by != request.user:
            return Response(
                {'error': "Vous ne pouvez supprimer que vos propres hôtels."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    # ── Action : toggle disponibilité ─────────────────────────────────────────

    @action(detail=True, methods=['patch'], url_path='toggle-disponibilite')
    def toggle_disponibilite(self, request, pk=None):
        """
        PATCH /api/hotels/{id}/toggle-disponibilite/
        Inverse la disponibilité sans modifier les autres champs.
        Réservé au créateur de l'hôtel.
        """
        hotel = self.get_object()
        if hotel.created_by != request.user:
            return Response(
                {'error': "Action non autorisée."},
                status=status.HTTP_403_FORBIDDEN
            )
        hotel.est_disponible = not hotel.est_disponible
        hotel.save(update_fields=['est_disponible'])
        etat = 'disponible' if hotel.est_disponible else 'indisponible'
        return Response({
            'id': hotel.id,
            'nom': hotel.nom,
            'est_disponible': hotel.est_disponible,
            'message': f'L\'hôtel "{hotel.nom}" est maintenant {etat}.',
        })

    # ── Action : statistiques globales ────────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='statistiques')
    def statistiques(self, request):
        """
        GET /api/hotels/statistiques/
        Statistiques sur l'ensemble des hôtels.
        """
        queryset = Hotel.objects.all()
        stats = queryset.aggregate(
            total_hotels=Count('id'),
            hotels_disponibles=Count('id', filter=Q(est_disponible=True)),
            prix_moyen=Avg('prix_par_nuit'),
            prix_min=Min('prix_par_nuit'),
            prix_max=Max('prix_par_nuit'),
            etoiles_moyenne=Avg('etoiles'),
            total_chambres=Sum('nombre_chambres'),
        )
        par_ville = (
            queryset
            .values('ville')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return Response({**stats, 'par_ville': list(par_ville)})
