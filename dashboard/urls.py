from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('metric/<int:metric_id>/note/', views.update_metric_note, name='update_metric_note'),
    path('api/metrics/live', views.live_metrics, name='live_metrics'),
]