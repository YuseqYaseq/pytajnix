# Generated by Django 2.2 on 2019-05-19 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_auto_20190519_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecturer',
            name='lectures',
            field=models.ManyToManyField(blank=True, related_name='lecturer_lecturers', to='application.Lecture'),
        ),
    ]
