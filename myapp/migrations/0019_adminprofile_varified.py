# Generated by Django 4.2.6 on 2023-11-08 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_rename_district_adminprofile_allocated_thana'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminprofile',
            name='varified',
            field=models.BooleanField(default=True),
        ),
    ]