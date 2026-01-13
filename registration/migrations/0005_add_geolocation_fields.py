# Generated migration for geolocation fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_collector_district_collector_province'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Latitude coordinate', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Longitude coordinate', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='collector',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Latitude coordinate', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='collector',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Longitude coordinate', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='collector',
            name='service_radius',
            field=models.DecimalField(decimal_places=2, default=10.0, help_text='Service radius in kilometers', max_digits=5),
        ),
        migrations.AddField(
            model_name='wastepickuprequest',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Pickup location latitude', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='wastepickuprequest',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Pickup location longitude', max_digits=9, null=True),
        ),
    ]

