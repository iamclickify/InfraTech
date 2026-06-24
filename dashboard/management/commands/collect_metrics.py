from django.core.management.base import BaseCommand
import logging

from dashboard.models import Metric
from dashboard.ssh_client import get_remote_metrics

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Collect system metrics from the remote Azure VM via SSH"

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("Fetching metrics from remote VM...")
            metrics = get_remote_metrics()

            Metric.objects.create(
                cpu=metrics["cpu"],
                ram=metrics["ram"],
                disk=metrics["disk"],
                uptime=metrics["uptime"]
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Azure VM metrics successfully collected and saved."
                )
            )
        except Exception as e:
            error_msg = f"Failed to collect metrics: {e}"
            logger.error(error_msg)
            self.stderr.write(
                self.style.ERROR(error_msg)
            )