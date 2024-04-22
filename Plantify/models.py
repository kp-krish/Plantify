from django.db import models

class Plants(models.Model):
    common_name=models.CharField(max_length=50)
    sci_name=models.CharField(max_length=50)
    image_url=models.CharField(max_length=30)
    desc=models.CharField(max_length=500)
    year=models.CharField(max_length=20)
    locations=models.CharField(max_length=500)
    
    def __str__(self):
        return self.product_name

