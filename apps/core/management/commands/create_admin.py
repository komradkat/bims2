from django.core.management.base import BaseCommand
from apps.core.models import User


class Command(BaseCommand):
    help = 'Create a test admin user for development'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = 'admin123'
        email = 'admin@bims.local'
        
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Password updated for existing user: {username}'))
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {username}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nLogin credentials:'))
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  URL: http://127.0.0.1:8000/login/')
