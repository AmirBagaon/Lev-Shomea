from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create Admin group with most permissions
        admin_group, created = Group.objects.get_or_create(name='Admins')
        admin_group.permissions.set(Permission.objects.all())
        
        # Create Super Admin group with all permissions  
        super_admin_group, created = Group.objects.get_or_create(name='Super Admins')
        super_admin_group.permissions.set(Permission.objects.all())
        
        self.stdout.write('✅ Groups created successfully!')