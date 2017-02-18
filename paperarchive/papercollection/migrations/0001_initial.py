# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=20, blank=True)),
                ('last_name', models.CharField(max_length=20, blank=True)),
                ('middle_name', models.CharField(max_length=20, blank=True)),
                ('full_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=75, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('organization', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('organization', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('year', models.IntegerField(blank=True)),
                ('volume', models.IntegerField(blank=True)),
                ('pages', models.CharField(max_length=100, blank=True)),
                ('month', models.CharField(max_length=15, blank=True)),
                ('doi', models.CharField(max_length=50, blank=True)),
                ('abstract', models.TextField(blank=True)),
                ('keywords', models.TextField(blank=True)),
                ('authors', models.ManyToManyField(to='papercollection.Author')),
                ('conference', models.ForeignKey(to='papercollection.Conference')),
                ('journal', models.ForeignKey(to='papercollection.Journal')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
