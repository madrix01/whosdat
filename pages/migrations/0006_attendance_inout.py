# Generated by Django 3.0.6 on 2020-06-17 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_attendanceout'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='inout',
            field=models.CharField(default=1, max_length=3),
            preserve_default=False,
        ),
    ]