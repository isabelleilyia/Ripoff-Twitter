# Generated by Django 3.0.8 on 2020-07-23 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_follower_like_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]
