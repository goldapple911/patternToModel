from django.db import models

class UploadedFile(models.Model):
    title = models.CharField(max_length=255)
    print(title)
    image = models.ImageField(upload_to='images/')
    file_3d = models.FileField(upload_to='3d_files/')
    # user_token = models.CharField(max_length=255)