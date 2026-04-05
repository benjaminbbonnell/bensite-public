from django.db import models

class WordSet(models.Model):
    set_code = models.CharField(max_length=100)
    set_name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Word Sets"

class Words(models.Model):
    word = models.CharField(max_length=100)
    word_set = models.ForeignKey(WordSet, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Words"