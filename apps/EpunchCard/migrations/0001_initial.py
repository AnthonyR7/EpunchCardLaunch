# Generated by Django 2.2 on 2019-05-08 20:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StaffMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PunchCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(99999), django.core.validators.MinValueValidator(0)])),
                ('day', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(365), django.core.validators.MinValueValidator(0)])),
                ('month', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(12), django.core.validators.MinValueValidator(0)])),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='EpunchCard.StaffMember')),
            ],
        ),
    ]
