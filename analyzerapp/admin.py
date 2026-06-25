# admin.py

from django.contrib import admin
from .models import Candidate, Resume
from django.utils.html import format_html

class ResumeAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'download_resume', 'uploaded_at')

    def download_resume(self, obj):
        if obj.resume_file:
            return format_html(
                '<a href="{}" download>📄 Download</a>',
                obj.resume_file.url
            )
        return "No file"
    download_resume.short_description = "Resume File"

class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'state', 'status']


admin.site.register(Candidate, CandidateAdmin)