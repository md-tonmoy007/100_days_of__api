# Generated by Django 4.2.10 on 2024-04-09 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_post_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='number',
            field=models.IntegerField(default=0),
        ),
    ]
