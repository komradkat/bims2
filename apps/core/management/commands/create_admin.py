from django.core.management.base import BaseCommand
import os
from apps.core.models import User


class Command(BaseCommand):
    help = 'Create a test admin user for development'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        if password == 'admin123':
            self.stdout.write(self.style.WARNING('Using default password "admin123". Set ADMIN_PASSWORD env var for security.'))
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
        
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write('  URL: http://127.0.0.1:8000/login/')
