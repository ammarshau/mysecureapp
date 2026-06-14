from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import User, Task, AuditLog
import datetime

# Helper functions
def log_activity(user, action, details, request):
    """Log user activities"""
    AuditLog.objects.create(
        user=user,
        action=action,
        details=details,
        ip_address=get_client_ip(request)
    )

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.role == 'admin'

# Public views
def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'core/register.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'core/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'core/register.html')
        
        user = User.objects.create_user(username=username, password=password)
        user.role = 'normal'
        user.save()
        
        login(request, user)
        log_activity(user, 'LOGIN_SUCCESS', f"User registered and logged in", request)
        messages.success(request, 'Registration successful!')
        return redirect('dashboard')
    
    return render(request, 'core/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            log_activity(user, 'LOGIN_SUCCESS', "User logged in", request)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            log_activity(None, 'LOGIN_FAILED', f"Failed login attempt for {username}", request)
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'core/login.html')

def user_logout(request):
    if request.user.is_authenticated:
        log_activity(request.user, 'LOGOUT', "User logged out", request)
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('home')

# Protected views
@login_required
def dashboard(request):
    tasks = Task.objects.filter(created_by=request.user)
    return render(request, 'core/dashboard.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        task = Task.objects.create(
            title=title,
            description=description,
            created_by=request.user
        )
        
        log_activity(request.user, 'TASK_CREATE', f"Created task: {title}", request)
        messages.success(request, 'Task created successfully!')
        return redirect('dashboard')
    
    return render(request, 'core/task_form.html')

@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if task.created_by != request.user and request.user.role != 'admin':
        return HttpResponseForbidden("You don't have permission to edit this task")
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.status = request.POST.get('status')
        task.save()
        
        log_activity(request.user, 'TASK_UPDATE', f"Updated task: {task.title}", request)
        messages.success(request, 'Task updated successfully!')
        return redirect('dashboard')
    
    return render(request, 'core/task_form.html', {'task': task})

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if task.created_by != request.user and request.user.role != 'admin':
        return HttpResponseForbidden("You don't have permission to delete this task")
    
    log_activity(request.user, 'TASK_DELETE', f"Deleted task: {task.title}", request)
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('dashboard')

@login_required
@user_passes_test(check_admin)
def admin_panel(request):
    """Admin panel with full monitoring"""
    users = User.objects.all()
    users_with_stats = []
    for user in users:
        users_with_stats.append({
            'user': user,
            'task_count': Task.objects.filter(created_by=user).count(),
        })
    
    all_tasks = Task.objects.all().order_by('-created_at')
    logs = AuditLog.objects.all().order_by('-timestamp')[:200]
    
    total_users = User.objects.count()
    total_tasks = Task.objects.count()
    total_logs = AuditLog.objects.count()
    admin_count = User.objects.filter(role='admin').count()
    completed_tasks = Task.objects.filter(status='completed').count()
    pending_tasks = Task.objects.filter(status='pending').count()
    
    context = {
        'users_with_stats': users_with_stats,
        'all_tasks': all_tasks,
        'logs': logs,
        'total_users': total_users,
        'total_tasks': total_tasks,
        'total_logs': total_logs,
        'admin_count': admin_count,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
    }
    
    return render(request, 'core/admin_panel.html', context)

@login_required
def audit_log_page(request):
    if request.user.role == 'admin':
        logs = AuditLog.objects.all().order_by('-timestamp')
    else:
        logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')
    
    return render(request, 'core/audit_log.html', {'logs': logs})

@login_required
def profile(request):
    return render(request, 'core/profile.html')

# Admin actions
@login_required
@user_passes_test(check_admin)
def make_admin(request, user_id):
    """Promote a normal user to admin"""
    user = User.objects.get(id=user_id)
    if user.role != 'admin':
        user.role = 'admin'
        user.save()
        log_activity(request.user, 'ADMIN_ACTION', f"Promoted {user.username} to admin", request)
        messages.success(request, f'{user.username} is now an admin!')
    else:
        messages.info(request, f'{user.username} is already an admin')
    return redirect('admin_panel')

@login_required
@user_passes_test(check_admin)
def delete_user(request, user_id):
    """Delete a user and all their tasks"""
    user = User.objects.get(id=user_id)
    username = user.username
    
    if user.role == 'admin':
        messages.error(request, 'Cannot delete admin users!')
    else:
        log_activity(request.user, 'ADMIN_ACTION', f"Deleted user {username} with all their tasks", request)
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
    
    return redirect('admin_panel')

@login_required
@user_passes_test(check_admin)
def admin_delete_task(request, task_id):
    """Admin can delete any task"""
    task = Task.objects.get(id=task_id)
    task_title = task.title
    task_owner = task.created_by.username
    
    log_activity(request.user, 'ADMIN_ACTION', f"Deleted task '{task_title}' owned by {task_owner}", request)
    task.delete()
    
    messages.success(request, f'Task "{task_title}" deleted successfully!')
    return redirect('admin_panel')