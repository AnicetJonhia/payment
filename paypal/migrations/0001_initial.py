# Generated by Django 5.2 on 2025-04-29 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('amount', models.PositiveIntegerField(help_text='Montant unitaire en cents (ex: 2000 = 20.00 USD)')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('paypal_order_id', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', help_text='Statut de la commande', max_length=10)),
                ('paid', models.BooleanField(default=False)),
                ('refunded', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'ordering': ['-created_at'],
            },
        ),
    ]
