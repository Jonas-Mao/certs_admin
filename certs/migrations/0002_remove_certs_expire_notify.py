# Generated by Django 3.2 on 2024-10-27 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certs',
            name='expire_notify',
        ),
    ]
