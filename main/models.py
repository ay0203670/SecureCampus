from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mainapp_uploaded_files')
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.file.name

class DownloadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mainapp_download_logs')
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='download_logs')
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} downloaded {self.file.file.name} on {self.timestamp}"