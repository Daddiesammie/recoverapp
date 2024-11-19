# Generated by Django 5.1.2 on 2024-11-18 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('JPY', 'Japanese Yen'), ('AUD', 'Australian Dollar'), ('CAD', 'Canadian Dollar')], default='USD', max_length=3),
        ),
    ]