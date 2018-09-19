# Generated by Django 2.1.1 on 2018-09-14 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Youtube', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ytcomment',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='posted_comments', to='Youtube.YTChannel'),
        ),
        migrations.AlterField(
            model_name='ytcomment',
            name='channel_target',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='comments', to='Youtube.YTChannel'),
        ),
        migrations.AlterField(
            model_name='ytcomment',
            name='parent_comment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='replies', to='Youtube.YTComment'),
        ),
        migrations.AlterField(
            model_name='ytcomment',
            name='video_target',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='comments', to='Youtube.YTVideo'),
        ),
        migrations.AlterField(
            model_name='ytplaylist',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='playlists', to='Youtube.YTChannel'),
        ),
        migrations.AlterField(
            model_name='ytvideo',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='videos', to='Youtube.YTChannel'),
        ),
    ]