from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from share import views as share_views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', share_views.home, name='home'),
    path('share/', include('share.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', share_views.user_dashboard, name='dashboard'),
    path('register/', share_views.register, name='register'),
    path('email-sent/', share_views.email_sent, name='email_sent'),
    path('download/<int:file_id>/', share_views.download_file, name='download_file'),
]
