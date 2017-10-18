from django.db import models

# Array of tuples lists the "Location" options
TOP_100_CITIES = (
    ("New York, NY", 'NY'),
    ("Chicago", 'CH'),
    ("Dallas, TX", 'DA'),
    ("LosAngeles, CA", 'LA'),
)


class Subscription(models.Model):
    email_address = models.EmailField(verbose_name="Email Address")
    location = models.CharField(max_length=20, choices=TOP_100_CITIES)

    def __str__(self):
        return self.email_address
