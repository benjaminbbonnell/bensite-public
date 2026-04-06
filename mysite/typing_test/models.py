from django.db import models

class WordSet(models.Model):
    set_code = models.CharField(max_length=100, primary_key=True)
    set_name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Word Sets"

class Words(models.Model):
    word_set = models.ForeignKey(WordSet, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    word_count = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "Words"