from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Supprime les utilisateurs inactifs inscrits depuis plus de 15 minutes.'

    def handle(self, *args, **options):

        time_threshold = timezone.now() - timedelta(minutes=15)

        inactive_users = User.objects.filter(
            is_active=False, 
            date_joined__lt=time_threshold
        )

        count = inactive_users.count()
        inactive_users.delete()

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Nettoyage terminé : {count} utilisateur(s) inactif(s) supprimé(s).'))
        else:
            self.stdout.write(self.style.NOTICE('Aucun utilisateur inactif à supprimer.'))
