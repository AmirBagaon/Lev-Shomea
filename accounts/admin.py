from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import format_html
from django import forms

# Import from the accounts app (current app)
from accounts.models import UserProfile
# Import from the shop app
from shop.models import Marketer

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form that includes all UserProfile fields"""
    
    # User fields
    first_name = forms.CharField(max_length=30, required=False, label='שם פרטי')
    last_name = forms.CharField(max_length=30, required=False, label='שם משפחה')
    email = forms.EmailField(required=False, label='כתובת דוא"ל')
    
    # UserProfile fields
    phone = forms.CharField(max_length=20, required=False, label='טלפון')
    phone2 = forms.CharField(max_length=20, required=False, label='טלפון נוסף')
    address = forms.CharField(max_length=200, required=False, label='כתובת')
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES, 
        initial='regular',
        label='סוג משתמש'
    )
    marketer = forms.ModelChoiceField(
        queryset=Marketer.objects.all(),
        required=False,
        label='משווק',
        empty_label='בחר משווק...'
    )
    is_active_profile = forms.BooleanField(
        initial=True, 
        required=False, 
        label='פעיל'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hebrew labels for base fields
        self.fields['username'].label = 'שם משתמש'
        self.fields['password1'].label = 'סיסמה'
        self.fields['password2'].label = 'אימות סיסמה'
        
        # Add CSS classes for better styling
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        # Save the User instance normally - the admin will handle UserProfile via save_model
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        
        # Set user active status from profile field
        user.is_active = self.cleaned_data.get('is_active_profile', True)
        
        if commit:
            user.save()
            
        return user

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'פרופיל משתמש מלא'
    fk_name = 'user'
    
    fieldsets = (
        ('פרטים אישיים', {
            'fields': ('phone', 'phone2', 'address'),
            'description': 'מידע ליצירת קשר וכתובת'
        }),
        ('הגדרות מכירה', {
            'fields': ('user_type', 'marketer', 'is_active'),
            'description': 'הגדרות הקשורות למכירות וניהול'
        }),
    )

class SimpleUserAdmin(BaseUserAdmin):
    """Simplified User Admin for charity use"""
    inlines = (UserProfileInline,)
    add_form = CustomUserCreationForm
    
    # Main list view - add phone to display
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_phone', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__phone')
    list_editable = ('is_active',)
    ordering = ('-date_joined',)
    
    # Edit form - simplified sections focused on login and permissions
    fieldsets = (
        ('פרטי התחברות', {
            'fields': ('username', 'first_name', 'last_name', 'email'),
            'description': 'פרטי המשתמש הבסיסיים'
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
            'classes': ('collapse',),
            'fields': ('is_superuser', 'groups', 'user_permissions'),
            'description': 'הגדרות מתקדמות - רק למנהל על'
        }),
        ('תאריכים', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    # Add form (when creating new user) - all details at once
    add_fieldsets = (
        ('פרטי המשתמש החדש', {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'),
            'description': 'פרטי התחברות ומידע בסיסי'
        }),
        ('פרטי קשר ומיקום', {
            'classes': ('wide',),
            'fields': ('phone', 'phone2', 'address'),
            'description': 'מידע ליצירת קשר'
        }),
        ('הגדרות מכירה וניהול', {
            'classes': ('wide',),
            'fields': ('user_type', 'marketer', 'is_active_profile', 'is_staff'),
            'description': 'הגדרות הקשורות למכירות ופעילות ומנהל: יכול לגשת לממשק הניהול'
        }),
    )
    
    readonly_fields = ('password_display', 'last_login', 'date_joined')
    
    def get_phone(self, obj):
        """Display phone in list view"""
        try:
            phones = []
            if obj.userprofile.phone:
                phones.append(obj.userprofile.phone)
            if obj.userprofile.phone2:
                phones.append(obj.userprofile.phone2)
            return ' / '.join(phones) if phones else '-'
        except UserProfile.DoesNotExist:
            return '-'
    get_phone.short_description = 'טלפון'
    
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
        """Change field labels to Hebrew and use custom creation form"""
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
            
        # Show warning when editing own account
        if obj and obj == request.user:
            form.base_fields['username'].help_text = '⚠️ אתה עורך את החשבון שלך - לא ניתן למחוק אותו'
        
        return form
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete users, but users cannot delete themselves"""
    
        # Users cannot delete themselves
        if obj and obj == request.user:
            return False
        
        if obj and obj.is_superuser:
            # Only superusers can delete other superusers
            return request.user.is_superuser
    
        # Regular admins can delete regular users and staff (but not themselves)
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
    
    def save_model(self, request, obj, form, change):
        """Override to save UserProfile data when creating new user"""
        print(f"DEBUG - save_model called, change={change}")
        print(f"DEBUG - Form type: {type(form)}")
        
        # First save the User object
        super().save_model(request, obj, form, change)
        
        # If this is a new user creation and we have our custom form
        if not change and isinstance(form, CustomUserCreationForm):
            print(f"DEBUG - Processing new user with custom form")
            print(f"DEBUG - Form data: {form.cleaned_data}")
            
            # Get or create UserProfile
            try:
                profile = obj.userprofile
                print(f"DEBUG - Found existing profile")
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=obj)
                print(f"DEBUG - Created new profile")
            
            # Update profile fields from form
            profile.phone = form.cleaned_data.get('phone', '')
            profile.phone2 = form.cleaned_data.get('phone2', '')
            profile.address = form.cleaned_data.get('address', '')
            profile.user_type = form.cleaned_data.get('user_type', 'regular')
            profile.marketer = form.cleaned_data.get('marketer', None)
            profile.is_active = form.cleaned_data.get('is_active_profile', True)
            profile.save()
            
            # Also update User.is_active to match profile
            obj.is_active = form.cleaned_data.get('is_active_profile', True)
            obj.save()
            
            print(f"DEBUG - Profile saved: phone={profile.phone}, user_type={profile.user_type}")
        else:
            print(f"DEBUG - Not processing (change={change}, form type={type(form)})")

    def response_add(self, request, obj, post_url_continue=None):
        """Custom response after adding a user"""
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        # Show success message
        self.message_user(request, f'המשתמש "{obj.username}" נוצר בהצלחה.')
        
        # Check which button was clicked
        if "_addanother" in request.POST:
            # "שמירה והוספת אחר" was clicked - redirect to add form
            return HttpResponseRedirect(reverse('admin:auth_user_add'))
        else:
            # Regular "שמירה" was clicked - redirect to change list
            return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Override to hide unwanted buttons"""
        extra_context = extra_context or {}
        
        # For add form (when object_id is None), hide the continue editing button
        if object_id is None:
            extra_context['show_save_and_continue'] = False
        
        return super().changeform_view(request, object_id, form_url, extra_context)

# Remove default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, SimpleUserAdmin)

# Updated UserProfile admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'user_type', 'phone', 'phone2', 'marketer', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'marketer', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone', 'phone2']
    list_editable = ['user_type', 'is_active']
    
    fieldsets = (
        ('משתמש', {
            'fields': ('user',)
        }),
        ('פרטים אישיים', {
            'fields': ('phone', 'phone2', 'address')
        }),
        ('הגדרות מכירה', {
            'fields': ('user_type', 'marketer', 'is_active')
        }),
    )