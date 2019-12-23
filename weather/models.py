from django.db import models
from django.contrib.auth.models import User
class City(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    name = models.CharField(max_length= 1000, null= True, blank= True)
    def __str__(self):
        return self.name
        
# Create your models here.
