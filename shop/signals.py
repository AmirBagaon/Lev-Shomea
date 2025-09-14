from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

@receiver(post_save, sender=User)
def assign_user_groups(sender, instance, **kwargs):
    """Auto-assign users to groups based on their status"""
    try:
        admin_group, created = Group.objects.get_or_create(name='Admins')
        super_admin_group, created = Group.objects.get_or_create(name='Super Admins')
        
        # Remove from all groups first
        instance.groups.clear()
        
        # Assign based on status
        if instance.is_superuser:
            instance.groups.add(super_admin_group)
        elif instance.is_staff:
            instance.groups.add(admin_group)
            
    except Exception:
        pass  # Groups will be created when needed