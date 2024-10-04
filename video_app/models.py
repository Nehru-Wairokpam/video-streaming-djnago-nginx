from django.db import models

# Create your models here.


class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    hls_master_url = models.URLField(max_length=500, null=True, blank=True)
    hls_360p_url = models.URLField(max_length=500, null=True, blank=True)
    hls_720p_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
