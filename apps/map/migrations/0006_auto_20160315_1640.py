# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-15 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0005_auto_20160315_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='unique_id',
            field=models.CharField(default=b'aac4a8c', max_length=8),
        ),
    ]
