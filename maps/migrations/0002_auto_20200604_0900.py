# Generated by Django 2.2.12 on 2020-06-04 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='layer',
            old_name='last_modified_by',
            new_name='modified_by',
        ),
        migrations.RenameField(
            model_name='layer',
            old_name='last_modified',
            new_name='modified_date',
        ),
        migrations.RemoveField(
            model_name='layer',
            name='boundary_field',
        ),
        migrations.RemoveField(
            model_name='layer',
            name='data_field',
        ),
        migrations.AddField(
            model_name='layer',
            name='admin_boundary_field',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='layer',
            name='value_field',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Value Field from the Table'),
        ),
    ]
