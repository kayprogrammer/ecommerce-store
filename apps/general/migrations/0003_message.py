# Generated by Django 4.0 on 2024-05-16 17:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0002_subscriber'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('addressed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]