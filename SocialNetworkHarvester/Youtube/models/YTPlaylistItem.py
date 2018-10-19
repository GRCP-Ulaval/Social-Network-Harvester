from django.db import models

from .YTPlaylist import YTPlaylist
from .YTVideo import YTVideo


class YTPlaylistItem(models.Model):
    playlist = models.ForeignKey(YTPlaylist, related_name='items', on_delete=models.CASCADE)
    video = models.ForeignKey(YTVideo, related_name='playlistsSpots', on_delete=models.CASCADE)
    playlistOrder = models.IntegerField(null=True)

    def get_fields_description(self):
        fields = {
            'playlistOrder': {
                'name': 'Position',
                'description': 'Position de la vidéo dans la liste de lecture'
            },
        }
        videoFields = YTVideo().get_fields_description()
        for key in videoFields:
            fields['video__%s' % key] = videoFields[key]
        return fields

    def get_obj_ident(self):
        return "YTPlaylistItem__%s" % self.pk

    class Meta:
        app_label = "Youtube"
        verbose_name = 'Élément de playlist Youtube'
        verbose_name_plural = 'Éléments de playlist Youtube'
