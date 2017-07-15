from django.db import models
from django import forms
from django.forms import ModelForm, Textarea

# Create your models here.

class Journal(models.Model):
    name = models.CharField(max_length = 100)
    organization = models.CharField(max_length = 100, blank = True)
    issn_number = models.CharField(max_length=50, blank=True)
    pub_type = models.CharField(max_length=100, blank=True)

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
    paper_volume = models.IntegerField(blank = True, null = True)
    paper_issue = models.IntegerField(blank = True, null = True)
    paper_number = models.CharField(max_length = 100, blank = True, null = True)
    paper_pages = models.CharField(max_length = 100, blank = True, null = True)
    paper_month = models.CharField(max_length = 15, blank = True, null = True)
    paper_doi = models.CharField(max_length = 50, blank = True, null = True)
    paper_abstract = models.TextField(blank = True, null = True)
    paper_keywords = models.TextField(blank = True, null = True)
    paper_journal = models.ForeignKey(Journal)
    paper_authors = models.ManyToManyField(Author, through = 'Contributor')
    paper_arnumber = models.CharField(max_length = 20, blank=True, null=True, \
                                    verbose_name="Article number")
    paper_url = models.URLField(blank=True, null=True, verbose_name="Paper URL")
    paper_pdflink = models.URLField(blank=True, null=True, verbose_name="PDF download link")

    def __unicode__(self):
        return self.paper_title


class Contributor(models.Model):
    author = models.ForeignKey(Author)
    paper = models.ForeignKey(Paper)
    position = models.IntegerField(default = 0)

    def __unicode__(self):
        return self.author.full_name + " wrote " + \
                self.paper.paper_title + " as " + \
                str(self.position) + " author"


class Institution(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name


class Affiliation(models.Model):
    institution = models.ForeignKey(Institution)
    author = models.ForeignKey(Author)
    year = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.author.full_name + " was associated with " + \
                self.institution.name + " in the year " + \
                str(self.year)


class PaperForm(ModelForm):
    class Meta:
        model = Paper
        fields = ('paper_title',
                  'paper_year',
                  'paper_volume',
                  'paper_number',
                  'paper_issue',
                  'paper_pages',
                  'paper_month',
                  'paper_doi',
                  'paper_arnumber',
                  'paper_abstract',
                  'paper_keywords',
                  'paper_url',
                  'paper_pdflink',
                  )
        widgets = {
            'paper_title': forms.TextInput(attrs={'size': 80}),
            'paper_doi': forms.TextInput(attrs={'size': 40}),
            'paper_url': forms.TextInput(attrs={'size': 80}),
            'paper_pdflink': forms.TextInput(attrs={'size': 80}),
            'paper_abstract': forms.Textarea(attrs={'rows': 15, 'cols': 80}),
            'paper_keywords': forms.Textarea(attrs={'rows': 15, 'cols': 80}),
            }


class JournalForm(ModelForm):
    class Meta:
        model = Journal
        fields = ('name',
                'organization')
        widgets = {
            'name': forms.TextInput(attrs={'size': 80}),
            'organization': forms.TextInput(attrs={'size': 60}),
            }


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'middle_name', 'full_name', 'email')

