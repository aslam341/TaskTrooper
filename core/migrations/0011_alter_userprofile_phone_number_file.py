# Generated by Django 4.2.1 on 2023-07-21 15:40

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=20, null=True, region=None),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='files/')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_files', to='core.project')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_files', to='core.task')),
            ],
        ),
    ]