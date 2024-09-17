# Generated by Django 4.0.8 on 2024-09-17 12:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus_number', models.CharField(blank=True, max_length=255, null=True)),
                ('capacity', models.PositiveIntegerField()),
                ('driver', models.ForeignKey(limit_choices_to={'is_driver': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_name', models.CharField(max_length=100)),
                ('description', models.TextField(default='No description available')),
                ('start_location', models.CharField(default='Unknown start location', max_length=255)),
                ('end_location', models.CharField(default='Unknown end location', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TransportRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transport_type', models.CharField(choices=[('pickup', 'Pickup'), ('dropoff', 'Drop-off'), ('both', 'Both Pickup and Drop-off')], max_length=20)),
                ('pickup_time', models.DateTimeField(blank=True, null=True)),
                ('pickup_location', models.CharField(blank=True, max_length=255, null=True)),
                ('dropoff_time', models.DateTimeField(blank=True, null=True)),
                ('dropoff_location', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentPickup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_location', models.CharField(max_length=255)),
                ('dropoff_location', models.CharField(max_length=255)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transportation.bus')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transportation.route')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.AddField(
            model_name='bus',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transportation.route'),
        ),
        migrations.AddField(
            model_name='bus',
            name='teachers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'is_teacher': True}, related_name='buses', to=settings.AUTH_USER_MODEL),
        ),
    ]
