# Generated by Django 2.2.12 on 2020-06-06 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0002_table_workspace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='create_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='table',
            name='update_date',
            field=models.DateTimeField(null=True),
        ),
    ]
