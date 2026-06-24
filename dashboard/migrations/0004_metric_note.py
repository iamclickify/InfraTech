from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_metric_uptime'),
    ]

    operations = [
        migrations.AddField(
            model_name='metric',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
