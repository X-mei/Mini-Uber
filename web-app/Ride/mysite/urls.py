"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from ride import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('ride/', include('ride.urls')),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
]




# path: 127.0.0.1 : 8000
# If user has already logged in, then display user's homepage.
# Otherwise, display a login form with a login form.

# 127.0.0.1: 8000/user/register/

