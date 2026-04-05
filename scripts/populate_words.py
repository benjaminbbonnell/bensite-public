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

def insertwords(word, word_set):
    Words.objects.create(word=word, word_set=word_set)

with open('words.txt', 'r') as file:
    for line in file:
        word = line.strip()
        word_set = WordSet.objects.get(id=1)
        insertwords(word, word_set)

print("Script complete")