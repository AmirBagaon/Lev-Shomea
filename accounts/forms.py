from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hebrew labels
        self.fields['username'].label = 'שם משתמש'
        self.fields['first_name'].label = 'שם פרטי'
        self.fields['last_name'].label = 'שם משפחה'
        self.fields['email'].label = 'אימייל'
        self.fields['password1'].label = 'סיסמה'
        self.fields['password2'].label = 'אישור סיסמה'