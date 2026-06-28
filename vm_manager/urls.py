from django.urls import path
from . import views

urlpatterns = [
    path('start', views.start_vm, name='vm_start'),
    path('stop', views.stop_vm, name='vm_stop'),
    path('restart', views.restart_vm, name='vm_restart'),
    path('deallocate', views.deallocate_vm, name='vm_deallocate'),
    path('status', views.get_status, name='vm_status'),
]
