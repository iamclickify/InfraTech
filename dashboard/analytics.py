from django.db.models import Avg, Max
from django.utils import timezone
from datetime import timedelta
from .models import Metric

def calculate_analytics():
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)
    twenty_four_hours_ago = now - timedelta(hours=24)

    # 1 hour aggregates
    hour_metrics = Metric.objects.filter(created_at__gte=one_hour_ago)
    hour_stats = hour_metrics.aggregate(
        avg_cpu=Avg('cpu'),
        avg_ram=Avg('ram'),
        avg_disk=Avg('disk')
    )

    # 24 hours aggregates
    day_metrics = Metric.objects.filter(created_at__gte=twenty_four_hours_ago)
    day_stats = day_metrics.aggregate(
        avg_cpu=Avg('cpu'),
        avg_ram=Avg('ram'),
        avg_disk=Avg('disk')
    )

    # Lifetime / Overall Peaks
    peaks = Metric.objects.aggregate(
        max_cpu=Max('cpu'),
        max_ram=Max('ram')
    )

    # Anomaly checks: Check last 10 records for CPU > 90% or RAM > 90%
    recent_10 = Metric.objects.order_by('-created_at')[:10]
    cpu_spikes = sum(1 for m in recent_10 if m.cpu > 90)
    ram_spikes = sum(1 for m in recent_10 if m.ram > 90)

    alerts = []
    
    # Check if VM is offline / metric collection is stale
    latest = Metric.objects.order_by('-created_at').first()
    if latest:
        time_diff = timezone.now() - latest.created_at
        if time_diff.total_seconds() > 120:
            minutes_ago = int(time_diff.total_seconds() // 60)
            alerts.append(f"Connection warning: Server is unreachable. Last active telemetry received {minutes_ago} minutes ago.")
        
        # Check if disk space is critical
        if latest.disk > 90:
            alerts.append(f"Disk space critical: {latest.disk}% partition space used.")
    else:
        alerts.append("No telemetry data has been received yet. Check your connection settings.")

    if cpu_spikes >= 2:
        alerts.append(f"High CPU alert: exceeded 90% in {cpu_spikes} recent logs.")
    if ram_spikes >= 2:
        alerts.append(f"High RAM alert: exceeded 90% in {ram_spikes} recent logs.")

    return {
        "hour_stats": {
            "cpu": round(hour_stats["avg_cpu"] or 0, 2),
            "ram": round(hour_stats["avg_ram"] or 0, 2),
            "disk": round(hour_stats["avg_disk"] or 0, 2),
        },
        "day_stats": {
            "cpu": round(day_stats["avg_cpu"] or 0, 2),
            "ram": round(day_stats["avg_ram"] or 0, 2),
            "disk": round(day_stats["avg_disk"] or 0, 2),
        },
        "peaks": {
            "cpu": round(peaks["max_cpu"] or 0, 2),
            "ram": round(peaks["max_ram"] or 0, 2),
        },
        "alerts": alerts
    }
