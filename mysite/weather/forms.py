from django import forms
from .models import Subscription


# User can subscribe for Weather-Powered-Email by providing email address and location to the "Subscription Form"
class SubscriptionForm(forms.ModelForm):

    # Meta class describes the input form based on the model object 'Subscription' from models.py
    class Meta:
        model = Subscription
        fields = (
            'email_address',
            'location',
        )


