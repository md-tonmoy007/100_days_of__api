# Generated by Django 4.2.16 on 2024-09-28 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_post_project'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='description',
        ),
    ]
