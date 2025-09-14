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
            'description': 'מנהל: יכול לגשת לממשק הניהול ולנהל את המערכת'
        }),
        ('הרשאות מתקדמות', {
            'classes': ('collapse',),  # This makes it collapsible
            'fields': ('is_superuser', 'groups', 'user_permissions'),
            'description': 'הגדרות מתקדמות - רק למנהל על'
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
    
    def get_fieldsets(self, request, obj=None):
        """Hide superuser field from non-superusers"""
        fieldsets = super().get_fieldsets(request, obj)
        
        # If current user is not superuser, hide superuser checkbox and groups
        if not request.user.is_superuser:
            new_fieldsets = []
            for name, data in fieldsets:
                # Remove superuser and groups fields from advanced permissions
                if name == 'הרשאות מתקדמות':
                    fields = list(data.get('fields', []))
                    # Remove is_superuser and groups from regular admins
                    if 'is_superuser' in fields:
                        fields.remove('is_superuser')
                    if 'groups' in fields:
                        fields.remove('groups')
                    if 'user_permissions' in fields:
                        fields.remove('user_permissions')
                    
                    # Only add the section if there are still fields left
                    if fields:
                        new_data = data.copy()
                        new_data['fields'] = tuple(fields)
                        new_data['description'] = 'הגדרות מתקדמות - מוגבל למנהל על בלבד'
                        new_fieldsets.append((name, new_data))
                else:
                    new_fieldsets.append((name, data))
            return new_fieldsets
        
        return fieldsets
    
    

    def get_form(self, request, obj=None, **kwargs):
        """Change field labels to Hebrew"""
        form = super().get_form(request, obj, **kwargs)
        
        # Change field labels to clearer Hebrew
        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].label = 'מנהל'
            form.base_fields['is_staff'].help_text = 'יכול לגשת לממשק הניהול ולנהל מוצרים והזמנות'
        
        if 'is_superuser' in form.base_fields:
            form.base_fields['is_superuser'].label = 'מנהל על'  
            form.base_fields['is_superuser'].help_text = 'הרשאות מלאות במערכת - יכול לנהל משתמשים ומנהלים'
            
            # Prevent users from removing their own superuser status
            if obj and obj == request.user and obj.is_superuser:
                form.base_fields['is_superuser'].disabled = True
                form.base_fields['is_superuser'].help_text = '⚠️ לא ניתן לבטל הרשאות "מנהל על" עבור עצמך (למניעת נעילה)'

        if 'is_active' in form.base_fields:
            form.base_fields['is_active'].label = 'פעיל'
            form.base_fields['is_active'].help_text = 'המשתמש יכול להתחבר למערכת'
        
        return form
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete users"""
        if obj and obj.is_superuser:
            # Only superusers can delete other superusers
            return request.user.is_superuser
        # Regular admins can delete regular users and staff
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Control who can edit which users"""
        if obj and obj.is_superuser and not request.user.is_superuser:
            # Regular admins cannot edit superusers
            return False
        return request.user.is_staff
    
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