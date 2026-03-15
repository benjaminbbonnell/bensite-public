from django.shortcuts import render, redirect

def index(request):

    return render(request, 'typing_test/typing_test.html')


def redirect_to_bensite_index(request):
    return redirect('bensite:index')