# Generated by Django 2.2.12 on 2020-06-18 06:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0004_auto_20200607_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltable',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 18, 6, 39, 55, 110706, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='table',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 18, 6, 39, 55, 110706, tzinfo=utc)),
        ),
    ]
