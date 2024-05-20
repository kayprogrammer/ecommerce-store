# Generated by Django 4.0 on 2024-05-16 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0003_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitedetail',
            name='map_url',
            field=models.URLField(default='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3001156.4288297426!2d-78.01371936852176!3d42.72876761954724!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4ccc4bf0f123a5a9%3A0xddcfc6c1de189567!2sNew%20York%2C%20USA!5e0!3m2!1sen!2sbd!4v1603794290143!5m2!1sen!2sbd', max_length=10000),
        ),
    ]