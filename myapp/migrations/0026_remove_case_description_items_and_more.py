# Generated by Django 4.2.6 on 2023-11-10 14:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_witness_alter_case_fir_witness_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case_description',
            name='items',
        ),
        migrations.RemoveField(
            model_name='case_fir',
            name='suspect_id',
        ),
        migrations.RemoveField(
            model_name='case_fir',
            name='witness_id',
        ),
        migrations.RemoveField(
            model_name='case_related',
            name='item',
        ),
        migrations.AddField(
            model_name='case_related',
            name='items',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='myapp.case_description'),
        ),
        migrations.AddField(
            model_name='physicalstructure',
            name='fir_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.case_fir'),
        ),
        migrations.AddField(
            model_name='witnessinfo',
            name='fir_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.case_fir'),
        ),
        migrations.AlterField(
            model_name='case_fir',
            name='case_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.case_related'),
        ),
        migrations.DeleteModel(
            name='witness',
        ),
    ]