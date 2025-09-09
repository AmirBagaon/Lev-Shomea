# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'פרופיל משתמש'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

# הסרת הרישום הקיים של User ורישום מחדש עם הפרופיל
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'user_type', 'phone', 'marketer', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'marketer', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    list_editable = ['user_type', 'is_active']
    
    fieldsets = (
        ('משתמש', {
            'fields': ('user',)
        }),
        ('פרטים', {
            'fields': ('phone', 'address')
        }),
        ('הגדרות', {
            'fields': ('user_type', 'marketer', 'is_active')
        }),
    )