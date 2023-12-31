# Generated by Django 4.2.6 on 2023-10-30 12:42

from django.db import migrations, models
import myapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_usertable_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('nid', models.CharField(max_length=20)),
                ('date_of_birth', models.DateField()),
                ('phone', models.CharField(max_length=15)),
                ('division', models.CharField(max_length=50)),
                ('district', models.CharField(max_length=50)),
                ('upazila', models.CharField(max_length=50)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to=myapp.models.filepath)),
            ],
        ),
    ]
