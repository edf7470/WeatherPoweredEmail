from django import forms
from .models import Subscription
from . import models
from weather.service import get_choices_array

# User can subscribe for Weather-Powered-Email by providing email address and location to the "Subscription Form"
class SubscriptionForm(forms.ModelForm):

    location = forms.ChoiceField(choices=get_choices_array(), label="Location",initial='Where do you live?',widget=forms.Select(),required=True)

    # Meta class describes the input form based on the model object 'Subscription' from models.py
    class Meta:
        model = Subscription
        fields = (
            'email_address',
            'location',
        )

    def clean(self):
        cleaned_data = super(SubscriptionForm, self).clean()
        email_address = cleaned_data.get("email_address")
        location = cleaned_data.get("location")
        return cleaned_data

    def clean_email_address(self):
        # Get the email
        email_address = self.cleaned_data.get('email_address')

        # Check to see if any users already exist with this email as a username.
        try:
            match = Subscription.objects.get(email_address=email_address)
        except Subscription.DoesNotExist:
            # Unable to find a user, this is fine
            return email_address

        print("Email address is already in use! - Validation ERROR")
        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')
