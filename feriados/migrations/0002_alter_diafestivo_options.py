# Generated by Django 4.0.4 on 2024-12-07 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feriados', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='diafestivo',
            options={'ordering': ['-fecha']},
        ),
    ]
