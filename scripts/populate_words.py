import os
import sys
from pathlib import Path

import django
from django.db import connection

project_root = Path(__file__).resolve().parent.parent / 'mysite'
sys.path.insert(0, str(project_root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

# flake8: noqa: E402
from typing_test.models import Words, WordSet

word_set_pk = 'english_standard'
word_set = WordSet.objects.get(pk=word_set_pk)

Words.objects.all().delete()

def insertwords(word, word_count, word_set):
    Words.objects.create(word=word, word_count=word_count, word_set=word_set)

with open('words.txt', 'r', encoding='utf-8-sig') as file:
    for line in file:
        word = line.strip().lower()
        word_count = word.count(" ") + 1
        insertwords(word, word_count, word_set)

connection.close()
print("Script complete")