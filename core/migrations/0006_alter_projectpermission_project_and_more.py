# Generated by Django 4.2.1 on 2023-06-24 08:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_projectpermission_delete_projectmembership_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectpermission',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='core.project'),
        ),
        migrations.AlterField(
            model_name='projectpermission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_permissions', to=settings.AUTH_USER_MODEL),
        ),
    ]