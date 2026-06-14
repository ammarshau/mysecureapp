from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/update/<int:task_id>/', views.task_update, name='task_update'),
    path('task/delete/<int:task_id>/', views.task_delete, name='task_delete'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('audit-log/', views.audit_log_page, name='audit_log'),
    path('profile/', views.profile, name='profile'),
    
    # ADMIN URLS - ADD THESE (they were missing)
    path('make-admin/<int:user_id>/', views.make_admin, name='make_admin'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete-task/<int:task_id>/', views.admin_delete_task, name='admin_delete_task'),
]