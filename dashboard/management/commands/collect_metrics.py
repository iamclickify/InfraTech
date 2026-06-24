from django.core.management.base import BaseCommand

import psutil

from dashboard.models import Metric


class Command(BaseCommand):

    help = "Collect system metrics"

    def handle(self, *args, **kwargs):
        from django.core.management.base import BaseCommand

from dashboard.models import Metric
from dashboard.ssh_client import get_remote_metrics


class Command(BaseCommand):

    help = "Collect system metrics"

    def handle(self, *args, **kwargs):

        metrics = get_remote_metrics()

        Metric.objects.create(
            cpu=metrics["cpu"],
            ram=metrics["ram"],
            disk=metrics["disk"],
            uptime=metrics["uptime"]
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Azure VM metrics saved"
            )
        )