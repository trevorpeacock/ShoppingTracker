# Generated by Django 3.1.7 on 2021-03-27 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(max_length=50)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('brand', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='LevelChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('change', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.stockitem')),
            ],
        ),
    ]
