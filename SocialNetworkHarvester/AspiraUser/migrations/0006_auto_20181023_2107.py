# Generated by Django 2.1.1 on 2018-10-23 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AspiraUser', '0005_itemharvester'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemharvester',
            old_name='harvest_from',
            new_name='harvest_since',
        ),
    ]
