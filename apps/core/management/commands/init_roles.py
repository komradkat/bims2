from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Initialize roles and groups'

    def handle(self, *args, **options):
        roles = ['Admin', 'Clerk', 'Treasurer']
        
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role}'))
            else:
                self.stdout.write(f'Group already exists: {role}')
                
        self.stdout.write(self.style.SUCCESS('Successfully initialized roles'))
