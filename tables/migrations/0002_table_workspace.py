# Generated by Django 2.2.12 on 2020-06-04 07:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_useractivation'),
        ('tables', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='table_workspace', to='core.Workspace'),
        ),
    ]
