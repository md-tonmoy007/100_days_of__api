# Generated by Django 4.2.10 on 2024-04-08 19:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0008_post_project_alter_post_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_by',
            field=models.ForeignKey(default='322e1edf75e643ca9c30039c07327af9', on_delete=django.db.models.deletion.CASCADE, related_name='project', to=settings.AUTH_USER_MODEL),
        ),
    ]
