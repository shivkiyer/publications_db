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
    if not request.method == "POST":
        return HttpResponseRedirect("/display-db/")
    else:
        if "paper_srno" in request.POST:
            paper_srno = int(request.POST["paper_srno"])
            edit_paper = Paper.objects.get(id = paper_srno)
            edit_paper_form = PaperForm(instance = edit_paper)
            author_list = edit_paper.paper_authors.all()
            author_form_list = []
            all_authors_in_db = Author.objects.all()
            other_author_list = []
            for author in author_list:
                author_form_entry = AuthorForm(instance = author)
                author_form_list.append([[], [], []])
                author_form_list[-1][0] = author_form_entry
                choices_for_author = []
                for other_authors in all_authors_in_db:
                    if not other_authors.id == author.id:
                        if author.full_name and other_authors.full_name:
                            if author.full_name.split()[-1] == other_authors.full_name.split()[-1]:
                                choices_for_author.append(other_authors)
                author_form_list[-1][1] = choices_for_author
                author_form_list[-1][2] = author

            journal = edit_paper.paper_journal
            journal_form = JournalForm(instance = journal)

        else:
            return HttpResponseRedirect("/display-db/")

    return render(request, "edit_paper.html", \
                    {'paper_id' : paper_srno,
                    'paper' : edit_paper_form,
                    'authors' : author_form_list,
                    'journal' : journal_form
                    },
                    context_instance = RequestContext(request))


def save_paper_data(paper_object, paper_form_data):
    paper_object.paper_title = paper_form_data["paper_title"]
    paper_object.paper_volume = paper_form_data["paper_volume"]
    paper_object.paper_number = paper_form_data["paper_number"]
    paper_object.paper_pages = paper_form_data["paper_pages"]
    paper_object.paper_month = paper_form_data["paper_month"]
    paper_object.paper_year = int(paper_form_data["paper_year"])
    paper_object.paper_doi = paper_form_data["paper_doi"]
    paper_object.paper_keywords = paper_form_data["paper_keywords"]
    paper_object.paper_abstract = paper_form_data["paper_abstract"]
    paper_object.save()

    return


def save_author_data(author_objects, author_form_data):
    for author_index in range(len(author_objects)):
        author = author_objects[author_index]
        if author_form_data[0][author_index]:
            author.full_name = author_form_data[0][author_index]
        if author_form_data[1][author_index]:
            author.first_name = author_form_data[1][author_index]
        if author_form_data[2][author_index]:
            author.last_name = author_form_data[2][author_index]
        if author_form_data[3][author_index]:
            author.middle_name = author_form_data[3][author_index]
        if author_form_data[4][author_index]:
            author.email = author_form_data[4][author_index]

        create_author_name = ""
        if author.first_name:
            create_author_name = create_author_name + author.first_name
        if author.middle_name:
            create_author_name = create_author_name + " " + author.middle_name
        if author.last_name:
            create_author_name = create_author_name + " " + author.last_name
        author.full_name = create_author_name
        author.save()

    return


def extract_author_forms(request):
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

    author_form_data = [full_name_received, \
                                    first_name_received, \
                                    last_name_received, \
                                    middle_name_received, \
                                    email_received]

    return author_form_data



def verify_paper(request):
    if request.method == 'POST':
        if "paper_srno" in request.POST:
            paper_extracted = Paper.objects.get(id = int(request.POST["paper_srno"]))
            list_of_authors = paper_extracted.paper_authors.all()
            journal_extracted = paper_extracted.paper_journal
            list_for_author_options = []
            for author in list_of_authors:
                list_for_author_options.append("authorcheck_" + str(author.id))

        if "paper_submit" in request.POST and request.POST["paper_submit"]=="Submit paper":
            print request.POST

            paper_submitted = PaperForm(request.POST)
            if paper_submitted.is_valid():
                paper_received = paper_submitted.cleaned_data
                save_paper_data(paper_extracted, paper_received)

            author_form_data = extract_author_forms(request)
            save_author_data(list_of_authors, author_form_data)

            journal_submitted = JournalForm(request.POST)
            if journal_submitted.is_valid():
                journal_received = journal_submitted.cleaned_data
                journal_extracted.name = journal_received["name"]
                if journal_received["organization"]:
                    journal_extracted.organization = journal_received["organization"]
                journal_extracted.save()

        for replace_author in list_for_author_options:
            if replace_author in request.POST and request.POST[replace_author]=="Check this author":
                print request.POST
                author_srno = int(replace_author.split("_")[1])
                print request.POST["otherauthors_" + str(author_srno)]

    return HttpResponse("Checking")




