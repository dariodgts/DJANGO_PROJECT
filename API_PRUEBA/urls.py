"""
URL configuration for API_PRUEBA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from API import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # SPA HTML Shell
    path('', views.index_view, name='index'),
    
    # API endpoints
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/auth/register/', views.api_register, name='api_register'),
    path('api/auth/logout/', views.api_logout, name='api_logout'),
    path('api/auth/user-info/', views.api_user_info, name='api_user_info'),
    
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/packages/', views.api_list_packages, name='api_list_packages'),
    path('api/checkout/', views.api_checkout, name='api_checkout'),
    
    path('api/projects/', views.api_list_projects, name='api_list_projects'),
    path('api/projects/<int:project_id>/', views.api_project_detail, name='api_project_detail'),
    
    path('api/tasks/create/', views.api_create_task, name='api_create_task'),
    path('api/tasks/<int:task_id>/update/', views.api_update_task, name='api_update_task'),
    path('api/tasks/<int:task_id>/delete/', views.api_delete_task, name='api_delete_task'),
    
    path('api/invoices/', views.api_list_invoices, name='api_list_invoices'),
    path('api/invoices/<int:invoice_id>/pay/', views.api_pay_invoice, name='api_pay_invoice'),
]
