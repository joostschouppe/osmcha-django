# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-11 20:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('changeset', '0048_changeset_area'),
    ]

    operations = [
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changeset', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='changeset.Changeset')),
            ],
            options={
                'verbose_name_plural': 'Priorities',
            },
        ),
    ]
