from django.db import models
from django.urls import reverse

from visor.models.tag import Tag


class Metadata(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year = models.CharField(max_length=20, blank=True)
    tags = models.ManyToManyField(Tag, related_name="images", blank=True)
    description = models.TextField(blank=True)
    museum = models.CharField(max_length=255, blank=True)
    material = models.CharField(max_length=255, blank=True)
    source = models.URLField(blank=True)

    def get_absolute_url(self):
        return reverse("visor:edit", args=[self.filename])

    def __str__(self):
        return f"{self.title} ({self.author})"
