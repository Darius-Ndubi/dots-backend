from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = 'Make the specified users staff'

    def handle(self, *args, **options):
        User.objects.filter(
            email='andrew.tc.pham@gmail.com'
        ).update(is_staff=True, is_superuser=True)
