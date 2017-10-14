from django.db import models


class Subscription(models.Model):
    email_address = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
