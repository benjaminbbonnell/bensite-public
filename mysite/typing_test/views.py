import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from .models import Words

def index(request):

    word_set_query = request.GET.get('word_set', 'english_standard')
    filtered_words = Words.objects.filter(word_set_id=word_set_query)
    all_ids = filtered_words.values_list('id', flat=True)
    sample_ids = random.sample(list(all_ids), 50)
    random_list = Words.objects.filter(id__in=sample_ids)
    word_list = random_list.values_list("word", flat=True)
    id_to_word = dict(zip([w.id for w in random_list], word_list))
    test_string = " ".join(id_to_word[id] for id in sample_ids)

    context = {
        'test_string': test_string

    }

    return render(request, 'typing_test/typing_test.html', context)


async def get_new_string(request):

    word_set_query = request.GET.get('word_set', 'english_standard')

    all_ids_list = await sync_to_async(list)(
        Words.objects.filter(word_set_id=word_set_query).values_list('id', flat=True)
    )
    
    sample_ids = random.sample(all_ids_list, k=50)
    
    words_data = await sync_to_async(list)(
        Words.objects.filter(id__in=sample_ids).values('id', 'word')
    )
    
    id_to_word = {item['id']: item['word'] for item in words_data}
    test_string = " ".join(id_to_word[id] for id in sample_ids)

    return JsonResponse({"new_string": test_string})


def redirect_to_bensite_index(request):
    return redirect('bensite:index')