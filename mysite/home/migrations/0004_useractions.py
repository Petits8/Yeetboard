# Generated by Django 2.0.7 on 2018-07-25 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20180724_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(default='<GUEST>', max_length=32)),
                ('action', models.CharField(max_length=256)),
                ('timestamp', models.DateTimeField()),
                ('ipv4', models.CharField(max_length=16)),
            ],
        ),
    ]
