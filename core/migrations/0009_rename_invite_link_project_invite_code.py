# Generated by Django 4.2.1 on 2023-06-24 22:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_task_users_alter_projectpermission_permission'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='invite_link',
            new_name='invite_code',
        ),
    ]