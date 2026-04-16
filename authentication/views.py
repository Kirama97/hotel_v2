from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserListSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
    AccountActivateSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()

def get_tokens_for_user(user):

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):

        time_threshold = timezone.now() - timedelta(minutes=15)
        User.objects.filter(is_active=False, date_joined__lt=time_threshold).delete()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserProfileSerializer(user).data,
            'message': 'Compte créé avec succès. Veuillez vérifier votre boîte mail pour l\'activer.',
        }, status=status.HTTP_201_CREATED)

class AccountActivateView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AccountActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.context['user']
        user.is_active = True
        user.activation_token = None
        user.save()
        return Response({'message': 'Compte activé avec succès. Vous pouvez maintenant vous connecter.'})

class LogoutView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Le champ "refresh" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'message': 'Déconnexion réussie.'},
            status=status.HTTP_205_RESET_CONTENT
        )

class UserProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):

        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class UserListView(generics.ListAPIView):

    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.annotate(
            total_hotels=Count('hotels')
        ).order_by('-date_joined')

class PasswordResetRequestView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.conf import settings
        from django.core.mail import send_mail

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = user.generate_reset_token()

            reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
            send_mail(
                subject='Réinitialisation de votre mot de passe',
                message=f'Bonjour {user.username},\n\nVous avez demandé à réinitialiser votre mot de passe. Cliquez sur le lien suivant :\n{reset_link}\n\nCe lien expire dans {getattr(settings, "PASSWORD_RESET_TOKEN_EXPIRY_HOURS", 1)} heure(s).',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({
                'message': 'Si cet email est associé à un compte, un email de réinitialisation a été envoyé.',
            })
        except User.DoesNotExist:
            return Response({
                'message': "Si cet email est associé à un compte, un email de réinitialisation a été envoyé.",
            })

class PasswordResetConfirmView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.context['user']
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        user.clear_reset_token()
        return Response({'message': 'Mot de passe réinitialisé avec succès.'})

class ChangePasswordView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'message': 'Mot de passe modifié avec succès.',
            'tokens': get_tokens_for_user(request.user),
        })
