# Generated by Django 2.2 on 2019-05-19 16:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_auto_20190519_0950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='question_creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='question',
            name='voters',
            field=models.ManyToManyField(blank=True, related_name='question_voters', through='application.QuestionVote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='questionvote',
            name='voter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questionvote_voter', to=settings.AUTH_USER_MODEL),
        ),
    ]
