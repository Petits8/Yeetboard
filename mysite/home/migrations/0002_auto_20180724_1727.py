# Generated by Django 2.0.7 on 2018-07-25 00:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='isNsfw',
        ),
        migrations.RemoveField(
            model_name='post',
            name='isSpoiler',
        ),
    ]
