from django.shortcuts import render
from .forms import SubscriptionForm


def index(request):
    form = SubscriptionForm()
    return render(request, 'weather\index.html', {'form': form})
