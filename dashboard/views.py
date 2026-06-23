from django.shortcuts import render
from .models import Metric
from django.utils import timezone

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

    context = {
        "latest_metric": latest_metric,
        "recent_metrics": recent_metrics,

        "labels": labels,
        "cpu_data": cpu_data,
        "ram_data": ram_data,
        "disk_data": disk_data,
    }

    return render(
        request,
        "dashboard/home.html",
        context
    )