# Generated by Django 3.2.8 on 2022-10-08 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0002_alter_user_userid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='userName',
            field=models.CharField(max_length=50),
        ),
    ]
