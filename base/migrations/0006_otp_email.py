# Generated by Django 4.2.5 on 2023-10-05 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_otp_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
