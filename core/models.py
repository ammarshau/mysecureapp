from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """Custom user model with role field and 2FA"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('normal', 'Normal User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')
    
    # 2FA Fields (add these)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_code = models.CharField(max_length=6, blank=True, null=True)
    two_factor_code_created = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.username

class Task(models.Model):
    """Task model for CRUD operations"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class AuditLog(models.Model):
    """Audit log for tracking activities"""
    ACTION_CHOICES = (
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('LOGOUT', 'Logout'),
        ('TASK_CREATE', 'Task Created'),
        ('TASK_UPDATE', 'Task Updated'),
        ('TASK_DELETE', 'Task Deleted'),
        ('ADMIN_ACTION', 'Admin Action'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"