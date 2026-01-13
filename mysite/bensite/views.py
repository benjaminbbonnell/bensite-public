from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone


def redirect_to_bensite_index(request):
    return redirect('bensite:index')

class IndexView(generic.ListView):
    template_name = 'bensite/index.html'

    def get_queryset(self):
        return []