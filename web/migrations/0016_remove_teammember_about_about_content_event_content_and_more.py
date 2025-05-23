# Generated by Django 4.2.21 on 2025-05-17 11:11

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0015_alter_review_options_review_avatar_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teammember',
            name='about',
        ),
        migrations.AddField(
            model_name='about',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='event',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='eventimage',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='gallery',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='project',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='review',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='toolimage',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='tools',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='vacancy',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='youtubeshort',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='services',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, default=''),
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='TeamMember',
        ),
    ]
