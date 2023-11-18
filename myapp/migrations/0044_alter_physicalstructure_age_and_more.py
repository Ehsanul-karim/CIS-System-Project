# Generated by Django 4.2.6 on 2023-11-18 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0043_case_fir_occurance_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalstructure',
            name='age',
            field=models.CharField(choices=[('MINOR', 'Minor'), ('YOUNG', 'Young'), ('ADULT', 'Adult'), ('AGED', 'Aged')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='physicalstructure',
            name='height',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='physicalstructure',
            name='weight',
            field=models.CharField(max_length=255),
        ),
    ]
