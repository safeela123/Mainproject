# Generated by Django 5.2 on 2025-06-13 07:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_question_alter_test_student_alter_payment_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='admission',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='app.admission'),
            preserve_default=False,
        ),
    ]
