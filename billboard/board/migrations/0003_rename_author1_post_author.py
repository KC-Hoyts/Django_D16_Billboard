# Generated by Django 4.2.6 on 2023-10-23 12:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0002_rename_author_post_author1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='author1',
            new_name='author',
        ),
    ]
