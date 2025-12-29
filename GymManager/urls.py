"""
URL configuration for GymManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from core.views import home, register, dashboard, membership_list, purchase_membership, reception_panel, toggle_visit, \
    class_schedule, create_class, signup_for_class, delete_class
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('memberships/', membership_list, name='membership_list'),
    path('memberships/buy/<int:membership_id>/', purchase_membership, name='purchase_membership'),
    path('reception/', reception_panel, name='reception_panel'),
    path('reception/toggle/<int:user_id>/', toggle_visit, name='toggle_visit'),
    path('schedule/', class_schedule, name='class_schedule'),
    path('schedule/add/', create_class, name='create_class'),
    path('schedule/delete/<int:class_id>/', delete_class, name='delete_class'),
    path('schedule/signup/<int:class_id>/', signup_for_class, name='signup_for_class'),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
