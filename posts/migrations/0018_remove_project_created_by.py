# Generated by Django 4.2.10 on 2024-04-10 05:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_project_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='created_by',
        ),
    ]