from django.db import models

# Create your models here.


class UploadedFile(models.Model):
    name = models.CharField(max_length=128)
    auth_token = models.CharField(max_length=128)
