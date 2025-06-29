# Generated by Django 5.2 on 2025-06-25 06:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_test_student_review_delete_drivingsession_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('lesson_type', models.CharField(choices=[('Classroom', 'Classroom'), ('Behind the Wheel', 'Behind the Wheel')], max_length=50)),
                ('time_in', models.TimeField()),
                ('time_out', models.TimeField()),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='admission',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='TestDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_type', models.CharField(choices=[('theory', 'Theory Test'), ('practical', 'Practical Test')], max_length=50)),
                ('test_date', models.DateField()),
                ('score', models.PositiveIntegerField()),
                ('passed', models.BooleanField(default=False)),
                ('attempt_number', models.PositiveIntegerField(default=1)),
                ('admission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='app.admission')),
            ],
        ),
    ]
