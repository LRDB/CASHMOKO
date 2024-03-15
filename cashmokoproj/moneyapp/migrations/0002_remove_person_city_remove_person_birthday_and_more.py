# Generated by Django 5.0.2 on 2024-03-15 02:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneyapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='City',
        ),
        migrations.RemoveField(
            model_name='person',
            name='birthday',
        ),
        migrations.AddField(
            model_name='person',
            name='email',
            field=models.EmailField(default='NAME@gmail.com', max_length=254),
        ),
        migrations.AddField(
            model_name='person',
            name='first_name',
            field=models.CharField(default='NAME', max_length=200),
        ),
        migrations.AddField(
            model_name='person',
            name='last_name',
            field=models.CharField(default='NAME', max_length=200),
        ),
        migrations.AddField(
            model_name='person',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
