# Generated by Django 5.0.6 on 2024-06-18 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_ranked', '0008_preference_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preference',
            name='rank',
            field=models.IntegerField(default=0),
        ),
    ]