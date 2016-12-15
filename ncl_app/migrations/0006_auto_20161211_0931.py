# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 14:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ncl_app', '0005_auto_20161210_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='day',
            name='name',
        ),
        migrations.RemoveField(
            model_name='match',
            name='name',
        ),
        migrations.AddField(
            model_name='day',
            name='number',
            field=models.IntegerField(default=0),
        ),
    ]
