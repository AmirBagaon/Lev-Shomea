# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """פרופיל משתמש מורחב"""
    
    USER_TYPE_CHOICES = [
        ('regular', 'רגיל'),
        ('admin', 'מנהל'),
        ('staff', 'צוות'),
        ('marketer', 'משווק'),
    ]
    
    # קישור למודל User הקיים של Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='משתמש')
    
    # פרטים נוספים
    phone = models.CharField(max_length=20, blank=True, verbose_name='טלפון')
    phone2 = models.CharField(max_length=20, blank=True, verbose_name='טלפון נוסף')  # NEW FIELD
    address = models.CharField(max_length=200, blank=True, verbose_name='כתובת')
    
    # סוג משתמש
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='regular', verbose_name='סוג משתמש')
    
    # משווק
    marketer = models.ForeignKey('shop.Marketer', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='משווק')
    
    # סטטוס
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    
    # תאריכים
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך הצטרפות')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='תאריך עדכון')
    
    class Meta:
        verbose_name = 'פרופיל משתמש'
        verbose_name_plural = 'פרופילי משתמשים'
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.get_user_type_display()}'
    
    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

# Signals remain the same
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)