from django.core.management.base import BaseCommand
from django.utils import timezone
from users.appointments.models import Appointment
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Eliminar appointments temporales expirados que no fueron pagados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué appointments serían eliminados sin eliminarlos realmente',
        )
        parser.add_argument(
            '--minutes',
            type=int,
            default=30,
            help='Minutos de expiración (default: 30)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        minutes = options['minutes']
        
        # Calcular la fecha límite
        expiry_threshold = timezone.now() - timezone.timedelta(minutes=minutes)
        
        # Buscar appointments temporales expirados
        expired_appointments = Appointment.objects.filter(
            is_temporary=True,
            payment_completed=False,
            expires_at__lt=expiry_threshold
        )
        
        count = expired_appointments.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay appointments expirados para eliminar.')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Se eliminarían {count} appointments expirados:'
                )
            )
            for appointment in expired_appointments:
                self.stdout.write(
                    f'  - Appointment #{appointment.id}: {appointment.service.title} '
                    f'(Expiró: {appointment.expires_at})'
                )
        else:
            # Eliminar appointments expirados
            deleted_count = expired_appointments.delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Se eliminaron {deleted_count} appointments expirados exitosamente.'
                )
            )
            
            # Log para auditoría
            logger.info(f'Se eliminaron {deleted_count} appointments expirados automáticamente') 