# Generated by Django 2.2.12 on 2020-06-18 07:53

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0005_auto_20200618_0639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltable',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 18, 7, 53, 53, 666189, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='table',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 18, 7, 53, 53, 666189, tzinfo=utc)),
        ),
    ]
