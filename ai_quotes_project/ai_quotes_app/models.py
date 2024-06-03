from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Quotes_DB(models.Model):
    quote = models.CharField(max_length=1000)
    author = models.CharField(max_length=500)
    category = models.CharField(max_length=500)

    def __str__(self):
        return f"Quotes written by {self.author}"


class UploadedPDF(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    pdf_file = models.FileField(max_length=5000,upload_to='pdf_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)