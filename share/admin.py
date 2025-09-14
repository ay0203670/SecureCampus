from django.contrib import admin
from .models import UploadedFile, DownloadLog
from django.utils.html import format_html

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'uploaded_at', 'download_link')

    def download_link(self, obj):
        return format_html(
            '<a href="{}" download>📥 Download</a>',
            obj.file.url
        )
    download_link.short_description = 'Download File'

@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_name', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user_username', 'file_file')

    def file_name(self, obj):
        return obj.file.file.name.split('/')[-1]
    file_name.short_description = 'File'