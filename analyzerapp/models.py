# analyzerapp/models.py

from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/uploaded/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Resume"

class Interview(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.TextField()
    video_file = models.FileField(upload_to='media/interviews/', null=True, blank=True)
    communication_score = models.IntegerField(default=0)
    relevance_score = models.IntegerField(default=0)
    confidence_score = models.IntegerField(default=0)
    total_score = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview for {self.user.username}"


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    state = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    interview_role = models.CharField(max_length=100, default='Frontend Developer')
    interview_duration = models.PositiveIntegerField(default=20)
    interview_question_count = models.PositiveIntegerField(default=15)
    
    resume_file = models.FileField(upload_to='resumes/uploaded/', null=True, blank=True)
    interview_video = models.FileField(upload_to='media/interviews/', null=True, blank=True)
    interview_transcript = models.TextField(blank=True)
    ai_result = models.TextField(blank=True)

    score = models.FloatField(default=0)
    status = models.CharField(max_length=20, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Resume(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='resumes')
    resume_file = models.FileField(upload_to='resumes/uploaded/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.name}'s Resume"


class UserFeedback(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='feedbacks')
    ai_rating = models.PositiveSmallIntegerField(default=3)
    platform_rating = models.PositiveSmallIntegerField(default=3)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.candidate.name}"
    
    
class Candidate1(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    state = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Pending')
    score = models.FloatField(default=0)
    interview_video = models.FileField(upload_to='media/interviews/', null=True, blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)  # ✅ Add this line

    def __str__(self):
        return self.name
