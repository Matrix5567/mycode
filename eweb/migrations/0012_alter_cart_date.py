# Generated by Django 4.0.4 on 2022-05-24 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eweb', '0011_rename_user_cart_customuser_alter_cart_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
