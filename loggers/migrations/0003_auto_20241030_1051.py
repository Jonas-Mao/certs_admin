# Generated by Django 3.2 on 2024-10-30 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggers', '0002_alter_logoperation_after'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='logscheduler',
            options={'ordering': ('-id',), 'verbose_name_plural': '定时任务日志'},
        ),
        migrations.RemoveField(
            model_name='logmonitor',
            name='update_time',
        ),
        migrations.RemoveField(
            model_name='logoperation',
            name='update_time',
        ),
        migrations.RemoveField(
            model_name='logscheduler',
            name='update_time',
        ),
    ]
