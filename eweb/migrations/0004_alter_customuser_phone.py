# Generated by Django 4.0.4 on 2022-05-12 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eweb', '0003_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
