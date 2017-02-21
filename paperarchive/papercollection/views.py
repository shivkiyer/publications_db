from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,  HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import backup_data
from papercollection.models import Author, Journal, Paper

# Create your views here.
def dbase_populate(request):
    # listing the articles
    collection_of_articles = backup_data.read_ref_file()
    for paper_item in collection_of_articles:
        new_paper_entry = Paper()
        new_paper_entry.paper_title = paper_item["title"]
        list_of_authors = paper_item["author"].split(" and ")
        print list_of_authors
        for author_entry in list_of_authors:
            while author_entry[0]==" ":
                author_entry = author_entry[1:]
            while author_entry[-1]==" ":
                author_entry = author_entry[:-1]
            new_author_item = Author()
            new_author_item.full_name = author_entry
            new_author_item.save()
            new_paper_entry.paper_authors = new_author_item

        if "journal" in paper_item.keys():
            new_journal_entry = Journal()
            new_journal_entry.name = paper_item["journal"]
            new_journal_entry.save()
            new_paper_entry.paper_journal = new_journal_entry
        if "booktitle" in paper_item.keys():
            new_journal_entry = Journal()
            new_journal_entry.name = paper_item["booktitle"]
            new_journal_entry.save()
            new_paper_entry.paper_journal = new_journal_entry
        if "year" in paper_item.keys():
            new_paper_entry.paper_year = paper_item["year"]
        if "volume" in paper_item.keys():
            new_paper_entry.paper_volume = paper_item["volume"]
        if "number" in paper_item.keys():
            new_paper_entry.paper_number = paper_item["number"]
        if "pages" in paper_item.keys():
            new_paper_entry.paper_pages = paper_item["pages"]
        if "year" in paper_item.keys():
            new_paper_entry.paper_year = paper_item["year"]
        if "abstract" in paper_item.keys():
            new_paper_entry.paper_abstract = paper_item["abstract"]
        if "doi" in paper_item.keys():
            new_paper_entry.paper_doi = paper_item["doi"]
        if "keywords" in paper_item.keys():
            new_paper_entry.paper_keywords = paper_item["keywords"]

        new_paper_entry.save()

    return HttpResponse("Hello again")
    

def dbase_display(request):
    collection_of_articles = Paper.objects.all()
    return render(request, "list_papers.html", \
                    {'collection_of_articles' : collection_of_articles},
                    context_instance = RequestContext(request))

