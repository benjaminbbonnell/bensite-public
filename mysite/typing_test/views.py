import random
from django.shortcuts import render, redirect
from .models import Words

def index(request):


    all_ids = Words.objects.values_list('id', flat=True)
    sample_ids = random.sample(list(all_ids), k=50)
    random_list = Words.objects.filter(id__in=sample_ids)
    word_list = random_list.values_list("word", flat=True)
    id_to_word = dict(zip([w.id for w in random_list], word_list))
    test_string = " ".join(id_to_word[id] for id in sample_ids)

    context = {
        'test_string': test_string

    }

    return render(request, 'typing_test/typing_test.html', context)


def redirect_to_bensite_index(request):
    return redirect('bensite:index')