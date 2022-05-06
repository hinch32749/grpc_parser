from django.db import models


class Article(models.Model):
    source_url = models.CharField(max_length=500)
    title = models.CharField(max_length=250)
    date_time = models.CharField(max_length=50, null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

