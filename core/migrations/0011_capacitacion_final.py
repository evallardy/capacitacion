# Generated by Django 4.0.4 on 2024-12-08 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_capacitacion_hora_inicial_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='capacitacion',
            name='final',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
