"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.urls import path
from .views import (
    LeituraUmidadeCreateAPI,
    ComandoPollAPI,
    ExecucaoConfirmAPI,
    AdminDispositivoCreateAPI,
    AdminConfigSetAPI,
    AdminComandoManualCreateAPI,
)

urlpatterns = [
    # Dispositivo
    path('iot/leituras/', LeituraUmidadeCreateAPI.as_view(), name='iot-leituras'),
    path('iot/comandos/', ComandoPollAPI.as_view(), name='iot-comandos'),
    path('iot/execucoes/', ExecucaoConfirmAPI.as_view(), name='iot-execucoes'),

    # Admin
    path('admin/dispositivos/', AdminDispositivoCreateAPI.as_view(), name='admin-dispositivos'),
    path('admin/dispositivos/<uuid:dispositivo_uuid>/config/', AdminConfigSetAPI.as_view(), name='admin-config'),
    path('admin/dispositivos/<uuid:dispositivo_uuid>/comandos/', AdminComandoManualCreateAPI.as_view(), name='admin-comando'),
]

