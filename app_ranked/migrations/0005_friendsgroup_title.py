# Generated by Django 5.0.6 on 2024-06-12 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_ranked', '0004_rename_rounds_vote_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendsgroup',
            name='title',
            field=models.CharField(default='Old Profile', max_length=100),
        ),
    ]