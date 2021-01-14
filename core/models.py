from django.db import models



class Talk(models.Model):
    title = models.CharField(max_length=100 , blank=False) 
    date = models.DateTimeField(blank=False)
    content = models.TextField(blank=False)
    capacity = models.IntegerField(blank=False)
    participant_count = models.IntegerField()

    def __str__(self):
        return self.title
    

class Workshop(models.Model):
    title = models.CharField(max_length=100 , blank=False) 
    date = models.DateTimeField(blank=False)
    content = models.TextField(blank=False)
    capacity = models.IntegerField(blank=False)
    participant_count = models.IntegerField()

    def __str__(self):
        return self.title
  
