# Generated by Django 3.1.13 on 2021-12-07 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='postuser',
            new_name='postuserid',
        ),
        migrations.AddField(
            model_name='post',
            name='postusername',
            field=models.CharField(default='admin', max_length=100),
        ),
        migrations.AlterField(
            model_name='post',
            name='poststatus',
            field=models.IntegerField(choices=[(1, 'DELIVERED'), (2, 'PENDING'), (0, 'BLOCKED')], default=1),
        ),
    ]
