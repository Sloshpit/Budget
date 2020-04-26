from django.db import models

class Category(models.Model):
    master_category = models.CharField(max_length=200, default='none')
    category = models.CharField(max_length=200)
    def __str__(self):
        return self.category
        