# Generated by Django 4.1.7 on 2023-03-28 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0010_navigationheaders_navsubheadings_queryreports'),
    ]

    operations = [
        migrations.AddField(
            model_name='queryreports',
            name='sub_sql_query',
            field=models.TextField(blank=True, null=True),
        ),
    ]
