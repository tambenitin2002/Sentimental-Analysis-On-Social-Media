from django.db import models

# Create your models here.
class demo(models.Model):
    images =  models.FileField(upload_to="images")
    text =  models.CharField(max_length =500)



class ImageModel(models.Model):
    image = models.ImageField(upload_to='Uploads')    