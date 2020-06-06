# Generated by Django 2.2.12 on 2020-06-06 11:31

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maplayer',
            name='create_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='maplayer',
            name='layer_colors',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='maplayer',
            name='modified_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='maplayer',
            name='tool_tip_fields',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), null=True, size=None),
        ),
    ]
