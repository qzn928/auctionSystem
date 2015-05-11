# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('lot', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('types', models.CharField(max_length=50)),
                ('sex', models.CharField(max_length=50)),
                ('customer_id', models.CharField(max_length=20)),
                ('size', models.CharField(max_length=20)),
                ('level', models.CharField(max_length=20)),
                ('color', models.CharField(max_length=20)),
                ('definition', models.CharField(max_length=20)),
                ('number', models.IntegerField()),
                ('final_price', models.IntegerField()),
                ('evaluation', models.CharField(max_length=100)),
                ('remarks', models.CharField(max_length=100)),
                ('is_invoice', models.IntegerField()),
                ('peel_inform', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('identifier', models.CharField(max_length=20)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invoice_nu', models.CharField(max_length=20)),
                ('customer_id', models.CharField(max_length=20)),
                ('goods_type', models.CharField(max_length=50)),
                ('goods_nu', models.IntegerField()),
                ('dollar_sum', models.IntegerField()),
                ('cost_sum', models.IntegerField()),
                ('auction_invoice', models.CharField(max_length=50)),
                ('final_exchange_rate', models.FloatField()),
                ('begin_exchange_rate', models.FloatField()),
                ('modify_times', models.IntegerField()),
                ('modify_date', models.DateField()),
                ('commodity', models.ForeignKey(to='auctionweb.Commodity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeelField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=150)),
                ('zip_code', models.CharField(max_length=10)),
                ('call_person', models.CharField(max_length=10)),
                ('call_phone', models.CharField(max_length=15)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='commodity',
            name='peel_field',
            field=models.ForeignKey(to='auctionweb.PeelField'),
            preserve_default=True,
        ),
    ]
