from django.contrib import admin
from django.urls import path
from core.views import test_endpoint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test/', test_endpoint, name='test_endpoint'),
]