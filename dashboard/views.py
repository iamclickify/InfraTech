from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Metric
from django.utils import timezone
from django.conf import settings
from .analytics import calculate_analytics

def home(request):

    latest_metric = Metric.objects.order_by(
        '-created_at'
    ).first()

    recent_metrics = Metric.objects.order_by(
        '-created_at'
    )[:10]

    chart_metrics = Metric.objects.order_by(
        '-created_at'
    )[:50]

    

    labels = []
    cpu_data = []
    ram_data = []
    disk_data = []

    for metric in reversed(chart_metrics):
        local_time = timezone.localtime(
            metric.created_at
        )   
        labels.append(
            local_time.strftime("%H:%M:%S")
        )

        cpu_data.append(metric.cpu)
        ram_data.append(metric.ram)
        disk_data.append(metric.disk)

    analytics = calculate_analytics()

    context = {
        "latest_metric": latest_metric,
        "recent_metrics": recent_metrics,
        "server_name": settings.SSH_VM_HOST,

        "labels": labels,
        "cpu_data": cpu_data,
        "ram_data": ram_data,
        "disk_data": disk_data,
        "analytics": analytics,
    }

    return render(
        request,
        "dashboard/home.html",
        context
    )


@require_POST
def update_metric_note(request, metric_id):
    metric = get_object_or_404(Metric, id=metric_id)
    note = request.POST.get('note', '').strip()
    metric.note = note if note else None
    metric.save()
    return redirect('home')