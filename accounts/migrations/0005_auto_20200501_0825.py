# Generated by Django 3.0.5 on 2020-05-01 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20200430_2346'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accountbalance',
            old_name='name',
            new_name='account',
        ),
    ]
