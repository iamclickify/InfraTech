from django.core.management.base import BaseCommand

import psutil

from dashboard.models import Metric


class Command(BaseCommand):

    help = "Collect system metrics"

    def handle(self, *args, **kwargs):

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        Metric.objects.create(
            cpu=cpu,
            ram=ram,
            disk=disk
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Metric saved"
            )
        )