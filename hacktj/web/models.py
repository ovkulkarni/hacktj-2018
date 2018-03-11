from django.db import models

# Create your models here.


class UploadedFile(models.Model):
    name = models.CharField(max_length=128)
    video_id = models.CharField(max_length=128)
    audio_data = models.CharField(max_length=4096 * 2 * 2 * 2, default="{}")
    video_data = models.CharField(max_length=4096 * 2 * 2 * 2, default="{}")
