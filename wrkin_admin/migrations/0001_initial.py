# Generated by Django 4.2.5 on 2023-10-23 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('email', models.TextField(blank=True, null=True)),
                ('role', models.IntegerField(blank=True, null=True)),
                ('country_code', models.IntegerField(blank=True, null=True)),
                ('phone_no', models.BigIntegerField(blank=True, null=True)),
                ('password', models.TextField(blank=True, null=True)),
                ('token', models.TextField(blank=True, null=True)),
                ('last_login_at', models.DateTimeField(blank=True, null=True)),
                ('last_updated_at', models.DateTimeField(blank=True, null=True)),
                ('is_enabled', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'admin_user',
            },
        ),
    ]
