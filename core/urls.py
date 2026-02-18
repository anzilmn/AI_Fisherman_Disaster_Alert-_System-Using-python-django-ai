from django.contrib import admin
from django.urls import path
from ai_engine.views import fisherman_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', fisherman_dashboard, name='home'),
]