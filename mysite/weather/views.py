from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect

from .forms import SubscriptionForm


def index(request):
    form = SubscriptionForm()
    return render(request, 'weather/index.html', {'form': form})


# subscribe 'view' takes action to save (or reject) the new subscription to the database, reroutes to results page
def subscribe(request):
    if request.POST:
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            # success represents whether or not the email_address is free to be used (true), or already in use and can't be reused (false)
            success = True
        else:
            success = False

        return render(request, 'weather/result.html', {'email_address': request.POST['email_address'], 'success': success,})

