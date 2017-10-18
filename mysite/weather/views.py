from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect

from .forms import SubscriptionForm
from .models import Subscription


def index(request):
    form = SubscriptionForm()
    return render(request, 'weather/index.html', {'form': form})


# subscribe 'view' takes action to save (or reject) the new subscription to the database, reroutes to results page
def subscribe(request):

    subscription = Subscription.objects.create(email_address=request.POST['email_address'], location=request.POST['location'])

    # success represents whether or not the user successfully subscribed (If that email address hasn't already been used)
    success = True;
    #  return render(request, 'weather/result.html')
    # return redirect(render('weather/result.html', kwargs={'email_address':subscription.email_address}))
    return HttpResponseRedirect(reverse('weather:result'))
    # , args=(subscription.email_address,
    # kwargs={'email_address':subscription.email_address, 'success':success,}
    # kwargs={'email_address':subscription.email_address, 'success':success,}


def result(request):
    return render(request, 'weather/result.html', {
    'email_address': Subscription.objects.get(pk=24)
  })
# 'email_address': Subscription.objects.get(pk=24)
