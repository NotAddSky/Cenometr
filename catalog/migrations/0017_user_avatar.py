# Generated by Django 4.2.20 on 2025-06-07 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0016_todotask'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
