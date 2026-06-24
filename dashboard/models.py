from django.db import models

class Metric(models.Model):
    cpu = models.FloatField()
    ram = models.FloatField()
    disk = models.FloatField()
    uptime = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at}"