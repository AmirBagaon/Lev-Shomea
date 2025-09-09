from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin)
def register(request):
    """Admin-only user registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'המשתמש {user.username} נוצר בהצלחה!')
            return redirect('/admin/auth/user/')  # Redirect to admin users list
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})