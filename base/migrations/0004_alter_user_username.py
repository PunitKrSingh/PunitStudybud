# Generated by Django 4.2.5 on 2023-10-05 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
