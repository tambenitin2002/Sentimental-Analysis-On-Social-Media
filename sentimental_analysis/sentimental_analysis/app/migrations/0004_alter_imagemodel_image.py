# Generated by Django 5.0.6 on 2024-05-25 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_imagemodel_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagemodel',
            name='image',
            field=models.FileField(upload_to='uploads'),
        ),
    ]
