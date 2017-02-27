from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,  HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import backup_data
from papercollection.models import Author, Journal, Paper
from papercollection.models import AuthorForm, JournalForm, PaperForm

# Create your views here.
def dbase_populate(request):
    # listing the articles
    collection_of_articles = backup_data.read_ref_file()
    for paper_item in collection_of_articles:
        list_of_authors = paper_item["author"].split(" and ")
        list_of_authors_in_paper = []
        for author_entry in list_of_authors:
            while author_entry[0]==" ":
                author_entry = author_entry[1:]
            while author_entry[-1]==" ":
                author_entry = author_entry[:-1]
            new_author_item = Author()
            new_author_item.full_name = author_entry
            new_author_item.save()
            list_of_authors_in_paper.append(new_author_item)

        if "journal" in paper_item.keys():
            new_journal_entry = Journal()
            new_journal_entry.name = paper_item["journal"]
            new_journal_entry.save()
        if "booktitle" in paper_item.keys():
            new_journal_entry = Journal()
            new_journal_entry.name = paper_item["booktitle"]
            new_journal_entry.save()

        new_paper_entry = Paper()
        new_paper_entry.paper_title = paper_item["title"]
        new_paper_entry.paper_journal = new_journal_entry
        new_paper_entry.save()
        for author_in_paper in list_of_authors_in_paper:
            new_paper_entry.paper_authors.add(author_in_paper)
            new_paper_entry.save()

        if "year" in paper_item.keys():
            new_paper_entry.paper_year = paper_item["year"]
        if "month" in paper_item.keys():
            new_paper_entry.paper_month = paper_item["month"]
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

    return HttpResponse("Database written.")
    

def dbase_display(request):
    collection_of_articles = Paper.objects.all()
    return render(request, "list_papers.html", \
                    {'collection_of_articles' : collection_of_articles},
                    context_instance = RequestContext(request))


def edit_paper(request):
    if "paper_srno" in request.POST:
        paper_srno = int(request.POST["paper_srno"])
        edit_paper = Paper.objects.get(id = paper_srno)
        edit_paper_form = PaperForm(instance = edit_paper)
        author_list = edit_paper.paper_authors.all()
        author_form_list = []
        for author in author_list:
            author_form_entry = AuthorForm(instance = author)
            author_form_list.append(author_form_entry)

        journal = edit_paper.paper_journal
        journal_form = JournalForm(instance = journal)

    return render(request, "edit_paper.html", \
                    {'paper_id' : paper_srno,
                    'paper' : edit_paper_form,
                    'authors' : author_form_list,
                    'journal' : journal_form
                    },
                    context_instance = RequestContext(request))


def verify_paper(request):
    if request.method == 'POST':

        if "paper_srno" in request.POST:
            paper_extracted = Paper.objects.get(id = int(request.POST["paper_srno"]))
        else:
            paper_extracted = Paper()

        paper_submitted = PaperForm(request.POST)
        if paper_submitted.is_valid():
            paper_received = paper_submitted.cleaned_data
            paper_extracted.paper_title = paper_received["paper_title"]
            paper_extracted.paper_volume = int(paper_received["paper_volume"])
            paper_extracted.paper_number = int(paper_received["paper_number"])
            paper_extracted.paper_pages = paper_received["paper_pages"]
            paper_extracted.paper_month = paper_received["paper_month"]
            paper_extracted.paper_year = int(paper_received["paper_year"])
            paper_extracted.paper_doi = paper_received["paper_doi"]
            paper_extracted.paper_keywords = paper_received["paper_keywords"]
            paper_extracted.paper_abstract = paper_received["paper_abstract"]
            paper_extracted.save()

        if "paper_srno" in request.POST:
            list_of_authors = paper_extracted.paper_authors.all()
            if "full_name" in request.POST:
                full_name_received = request.POST.getlist("full_name")
            if "first_name" in request.POST:
                first_name_received = request.POST.getlist("first_name")
            if "last_name" in request.POST:
                last_name_received = request.POST.getlist("last_name")
            if "middle_name" in request.POST:
                middle_name_received = request.POST.getlist("middle_name")
            if "email" in request.POST:
                email_received = request.POST.getlist("email")
            for author_index in range(len(list_of_authors)):
                author = list_of_authors[author_index]
                author.full_name = full_name_received[author_index]
                author.first_name = first_name_received[author_index]
                author.last_name = last_name_received[author_index]
                author.middle_name = middle_name_received[author_index]
                author.email = email_received[author_index]
                author.save()

    return HttpResponse("Checking")




