from django.db import models


class Subscription(models.Model):
    email_address = models.EmailField()
    location = models.CharField(max_length=200)
