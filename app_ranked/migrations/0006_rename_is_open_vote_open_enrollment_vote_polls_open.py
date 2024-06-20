# Generated by Django 5.0.6 on 2024-06-12 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_ranked', '0005_friendsgroup_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='is_open',
            new_name='open_enrollment',
        ),
        migrations.AddField(
            model_name='vote',
            name='polls_open',
            field=models.BooleanField(default=True),
        ),
    ]
