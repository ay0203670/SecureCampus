from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'share'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('login/', auth_views.LoginView.as_view(template_name='share/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.file_list, name='file_list'),
    path('files/<int:file_id>/', views.file_detail, name='file_detail'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('files/<int:file_id>/download/', views.download_file, name='download_file'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('email-sent/', views.email_sent, name='email_sent'),
]
