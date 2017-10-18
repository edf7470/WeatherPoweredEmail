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

    def clean_email(self):
        # Get the email
        email_address = self.cleaned_data.get('email_address')

        # Check to see if any users already exist with this email as a username.
        try:
            match = Subscription.objects.get(email_address=email_address)
        except Subscription.DoesNotExist:
            # Unable to find a user, this is fine
            return email_address

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')


