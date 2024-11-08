from django.db import models

# Create your models here.

class userfiles(models.Model):
    title = models.TextField()
    file_data = models.FileField(upload_to='documents/')

    def __str__(self):
        return self.title