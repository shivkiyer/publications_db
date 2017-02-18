from django.db import models
from django import forms
from django.forms import ModelForm, Textarea

# Create your models here.


class Author(models.Model):
    first_name = models.CharField(max_length = 20, blank = True)
    last_name = models.CharField(max_length = 20, blank = True)
    middle_name = models.CharField(max_length = 20, blank = True)
    full_name = models.CharField(max_length = 50)
    email = models.EmailField(blank = True)

    def __unicode__(self):
        return self.full_name


class Journal(models.Model):
    name = models.CharField(max_length = 100)
    organization = models.CharField(max_length = 100, blank = True)

    def __unicode__(self):
        return name



class Conference(models.Model):
    name = models.CharField(max_length = 100)
    organization = models.CharField(max_length = 100, blank = True)

    def __unicode__(self):
        return name



class Paper(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    journal = models.ForeignKey(Journal)
    conference = models.ForeignKey(Conference)
    year = models.IntegerField(blank = True)
    volume = models.IntegerField(blank = True)
    pages = models.CharField(max_length = 100, blank = True)
    month = models.CharField(max_length = 15, blank = True)
    doi = models.CharField(max_length = 50, blank = True)
    abstract = models.TextField(blank = True)
    keywords = models.TextField(blank = True)
        
    def __unicode__(self):
        return self.title


