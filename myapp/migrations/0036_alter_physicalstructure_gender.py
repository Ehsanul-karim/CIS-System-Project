# Generated by Django 4.2.6 on 2023-11-10 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0035_alter_case_fir_crime_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalstructure',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')], max_length=255, null=True),
        ),
    ]
