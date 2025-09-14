from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, FileResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import UploadFileForm, RegisterForm
from .models import UploadedFile

# HOME PAGE
def home(request):
    if request.user.is_authenticated:
        return redirect('share:dashboard')
    return render(request, 'share/home.html')

# REGISTER
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(request, user)
            messages.success(request, 'Please check your email to complete registration')
            return redirect('share:email_sent')
    else:
        form = RegisterForm()
    return render(request, 'share/register.html', {'form': form})

# SEND EMAIL VERIFICATION
def send_verification_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('share/email_verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

# VERIFY EMAIL
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Account verified successfully!')
        return redirect('share:dashboard')
    messages.error(request, 'Invalid activation link')
    return redirect('home')

# LOGIN
def login_view(request):
    if request.method == 'POST':
        from django.contrib.auth import authenticate  # ✅ imported inside function
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('share:dashboard')
            else:
                messages.error(request, 'Your account is not active. Please verify your email.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'share/login.html')

# LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('share:home')

# FILE UPLOAD
@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        UploadedFile.objects.create(user=request.user, file=uploaded_file)
        messages.success(request, '✅ File uploaded successfully.')
        return redirect('share:file_list')
    return render(request, 'share/upload.html')

# FILE LIST
@login_required
def file_list(request):
    files = UploadedFile.objects.filter(user=request.user)
    return render(request, 'share/file_list.html', {'files': files})

# FILE DETAIL
@login_required
def file_detail(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    return render(request, 'share/file_detail.html', {'file': file})

# DELETE FILE
@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    if request.method == 'POST':
        file.delete()
        messages.success(request, "File deleted successfully")
        return redirect('share:file_list')
    return render(request, 'share/confirm_delete.html', {'file': file})

# DOWNLOAD FILE
@login_required
def download_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    if request.user != file.user and not request.user.is_staff:
        messages.error(request, "Unauthorized access")
        return redirect('share:file_list')
    return FileResponse(file.file.open('rb'), as_attachment=True, filename=file.file.name)

# DASHBOARD
@login_required
def user_dashboard(request):
    recent_files = UploadedFile.objects.filter(
        user=request.user
    ).order_by('-uploaded_at')[:5]
    
    context = {
        'recent_files': recent_files,
        'file_count': UploadedFile.objects.filter(user=request.user).count(),
        'storage_used': sum(f.file.size for f in recent_files) / (1024 * 1024)  # MB
    }
    return render(request, 'share/dashboard.html', context)
# EMAIL SENT PAGE
def email_sent(request):
    return render(request, 'share/email_sent.html')
