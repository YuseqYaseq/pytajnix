# Generated by Django 2.2 on 2019-05-19 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0003_auto_20190519_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecturer',
            name='name',
            field=models.CharField(max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='lecturer',
            name='surname',
            field=models.CharField(max_length=120, null=True),
        ),
    ]
