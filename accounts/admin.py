# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'פרטים נוספים'
    fk_name = 'user'
    fields = ('phone', 'address', 'user_type', 'marketer', 'is_active')

class SimpleUserAdmin(BaseUserAdmin):
    """Simplified User Admin for charity use"""
    inlines = (UserProfileInline,)
    
    # Main list view
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_editable = ('is_active',)
    ordering = ('-date_joined',)
    
    # Edit form - simplified sections
    fieldsets = (
        ('פרטי משתמש', {
            'fields': ('username', 'first_name', 'last_name', 'email')
        }),
        ('סיסמה', {
            'fields': ('password_display',),
            'description': 'השתמש בקישור "שנה סיסמה" למטה כדי לשנות את הסיסמה.'
        }),
        ('הרשאות', {
            'fields': ('is_active', 'is_staff'),
            'description': 'is_active: המשתמש יכול להתחבר | is_staff: המשתמש יכול לגשת לממשק הניהול'
        }),
        ('הרשאות מתקדמות', {
            'classes': ('collapse',),  # This makes it collapsible
            'fields': ('is_superuser', 'groups', 'user_permissions'),
            'description': 'הגדרות מתקדמות - בדרך כלל לא צריך לשנות'
        }),
        ('תאריכים', {
            'classes': ('collapse',),  # This makes it collapsible
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    # Add form (when creating new user)
    add_fieldsets = (
        ('צור משתמש חדש', {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
        ('הרשאות', {
            'fields': ('is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ('password_display', 'last_login', 'date_joined')
    
    def password_display(self, obj):
        """Show a user-friendly password field with change password link"""
        if obj.pk:  # Only show for existing users
            change_password_url = f'/admin/auth/user/{obj.pk}/password/'
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6;">'
                '<strong>הסיסמה מוגנת ומוצפנת</strong><br>'
                '<a href="{}" class="button" style="margin-top: 8px; display: inline-block;">שנה סיסמה</a>'
                '</div>',
                change_password_url
            )
        else:
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6;">'
                '<strong>הגדר סיסמה בעת יצירת המשתמש</strong>'
                '</div>'
            )
    password_display.short_description = 'סיסמה'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Remove default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, SimpleUserAdmin)

# Optional: Also register UserProfile separately if you want
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
        ('פרטים נוספים', {
            'fields': ('phone', 'address')
        }),
        ('הגדרות מכירה', {
            'fields': ('user_type', 'marketer', 'is_active')
        }),
    )