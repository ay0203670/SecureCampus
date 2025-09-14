from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import UploadedFile
from .forms import CustomRegistrationForm  # Assuming you have this

# Homepage View
def home(request):
    """Render the homepage with login/register options"""
    return render(request, 'share/home.html')

# Registration View (moved from URLs)
def register(request):
    """Handle custom user registration"""
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomRegistrationForm()
    return render(request, 'share/register.html', {'form': form})

# Email Verification View
def verify_email(request, uidb64, token):
    """Handle email verification"""
    # ... your existing email verification logic ...
    return render(request, 'share/verify_email.html', context)

# File Operations (all require login)
@login_required
def download_file(request, file_id):
    """Download a specific file"""
    uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    return FileResponse(uploaded_file.file.open(), as_attachment=True)

@login_required
def upload_file(request):
    """Handle file uploads"""
    if request.method == 'POST':
        # ... your existing upload logic ...
        return redirect('file_list')
    return render(request, 'share/upload.html')

@login_required
def file_list(request):
    """List all user's files"""
    files = UploadedFile.objects.filter(user=request.user)
    return render(request, 'share/file_list.html', {'files': files})

@login_required
def delete_file(request, file_id):
    """Delete a specific file"""
    file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    if request.method == 'POST':
        file.delete()
        return redirect('file_list')
    return render(request, 'share/confirm_delete.html', {'file': file})

@login_required
def user_dashboard(request):
    """User dashboard view"""
    user_files = UploadedFile.objects.filter(user=request.user)[:5]  # Recent files
    context = {
        'user': request.user,
        'recent_files': user_files
    }
    return render(request, 'share/dashboard.html', context)