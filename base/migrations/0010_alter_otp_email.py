# Generated by Django 4.2.5 on 2023-10-05 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_otp_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
