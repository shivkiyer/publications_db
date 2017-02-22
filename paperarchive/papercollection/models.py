from django.db import models
from django import forms
from django.forms import ModelForm, Textarea

# Create your models here.

class Journal(models.Model):
    name = models.CharField(max_length = 100)
    organization = models.CharField(max_length = 100, blank = True)

    def __unicode__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length = 20, blank = True)
    last_name = models.CharField(max_length = 20, blank = True)
    middle_name = models.CharField(max_length = 20, blank = True)
    full_name = models.CharField(max_length = 50)
    email = models.EmailField(blank = True)

    def __unicode__(self):
        return self.full_name


class Paper(models.Model):
    paper_title = models.CharField(max_length=200)
    paper_year = models.IntegerField(blank = True, null = True)
    paper_volume = models.CharField(max_length = 100,blank = True, null = True)
    paper_number = models.CharField(max_length = 100,blank = True, null = True)
    paper_pages = models.CharField(max_length = 100, blank = True, null = True)
    paper_month = models.CharField(max_length = 15, blank = True, null = True)
    paper_doi = models.CharField(max_length = 50, blank = True, null = True)
    paper_abstract = models.TextField(blank = True, null = True)
    paper_keywords = models.TextField(blank = True, null = True)
    paper_journal = models.ForeignKey(Journal)
    paper_authors = models.ManyToManyField(Author)

    def __unicode__(self):
        return self.paper_title


#class Conference(models.Model):
#    name = models.CharField(max_length = 100)
#    organization = models.CharField(max_length = 100, blank = True)
#
#    def __unicode__(self):
#        return name
