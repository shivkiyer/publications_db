from django.views.generic import View
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,  HttpResponseRedirect
from django.template import RequestContext
import backup_data
import models
from papercollection.models import Author, Journal, Paper, Contributor
from papercollection.models import AuthorForm, JournalForm, PaperForm
import urllib2
from django.db import connection


def index(request):
    return render(request, "index.html")


def dbase_display(request):
    return render(request, "browse_choices.html")


def insert_articles_into_db(collection_of_articles):
    """
    Insert a dictionary of publications into separate database rows.
    """
    
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
        author_position = 1
        for author_in_paper in list_of_authors_in_paper:
            paper_contributor = Contributor(paper = new_paper_entry,
                                            author = author_in_paper,
                                            position = author_position)
            author_position += 1
            paper_contributor.save()
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
        print(new_paper_entry.id)

    return

def insert_articles_from_web(collection_of_articles):
    """
    Insert a dictionary of publications into separate database rows.
    """

    paper_search_fields = ["title", "authors", "affiliations", "pubtitle", "punumber", \
                    "pubtype", "publisher", "volume", "issue", "py", "spage", \
                    "epage", "abstract", "issn", "arnumber", "doi", "publicationId", \
                    "partnum", "mdurl", "pdf", "term", "month"]
    journal_search_fields = ["pubtitle", "pubtype", "publisher","issn"]

    paper_count = 1
    author_count = 1
    journal_count = 1
#    institution_count = 1
    
    all_paper_list = []
    all_author_list = []
    all_journal_list = []
    paper_models = []
    author_models = []
    journal_models = []
    for paper_item in collection_of_articles:
        paper_record = {}
        journal_record = {}
        author_record = {}
        keys_in_paper_item = paper_item.keys()
        for search_item in paper_search_fields:
            if not (search_item=="spage" or \
                    search_item=="epage" or \
                    search_item=="term" or \
                    search_item=="publicationId" or \
                    search_item=="partnum" or \
                    search_item=="arnumber"
                    ):
                if search_item in keys_in_paper_item:
                    paper_record[search_item] = paper_item[search_item]
                else:
                    paper_record[search_item] = ""
                print(search_item, paper_record[search_item])
        if "spage" in keys_in_paper_item:
            paper_record["pages"] = paper_item["spage"]+"-"
        else:
            paper_record["pages"] = "-"
        if "epage" in keys_in_paper_item:
            paper_record["pages"] += paper_item["epage"]
        if "term" in keys_in_paper_item:
            paper_record["keywords"] = ""
            for term_item in paper_item["term"]:
                paper_record["keywords"] += term_item + ", "
            paper_record["keywords"] = paper_record["keywords"][:-2]
        else:
            paper_record["keywords"] = ""
        if "publicationId" in keys_in_paper_item:
            paper_record["arnumber"] = paper_item["publicationId"]
        elif "partnum" in keys_in_paper_item:
            paper_record["arnumber"] = paper_item["partnum"]
        elif "arnumber" in keys_in_paper_item:
            paper_record["arnumber"] = paper_item["arnumber"]

        for search_item in journal_search_fields:
            journal_record[search_item] = paper_item[search_item]

        paper_model_item = models.Paper(paper_title=paper_record["title"], \
                                        paper_year=paper_record["py"], \
                                        paper_volume=paper_record["volume"], \
                                        paper_issue=paper_record["issue"], \
                                        paper_number=paper_record["punumber"], \
                                        paper_pages=paper_record["pages"], \
                                        paper_month=paper_record["month"], \
                                        paper_doi=paper_record["doi"], \
                                        paper_abstract=paper_record["abstract"], \
                                        paper_keywords=paper_record["keywords"], \
                                        paper_journal=paper_record["pubtitle"], \
                                        paper_authors=paper_record["authors"], \
                                        paper_arnumber=paper_record["arnumber"], \
                                        paper_url=paper_record["mdurl"], \
                                        paper_pdflink=paper_record["pdf"], \
                                        publisher_organization=paper_record["publisher"], \
                                        publisher_issn_number=paper_record["issn"], \
                                        publisher_type=paper_record["pubtype"]
                            )
        paper_models.append(paper_model_item)
        all_paper_list.append(paper_record)
        paper_count += 1

        journal_model_item = models.Journal(name=paper_record["pubtitle"], \
                                            organization=paper_record["publisher"], \
                                            issn_number=paper_record["issn"], \
                                            pub_type=paper_record["pubtype"]
                            )
        journal_models.append(journal_model_item)
        all_journal_list.append(journal_record)
        journal_count += 1

        list_of_authors = paper_item["authors"].split(";")
        list_of_authors_in_paper = ""
        for count, author_entry in enumerate(list_of_authors):
            author_entry = author_entry.strip()
            author_record["full_name"] = author_entry
            all_author_list.append(author_record)
            author_model_item = models.Author(full_name=author_record["full_name"])
            author_models.append(author_model_item)
            author_count += 1
            list_of_authors_in_paper += author_entry
            if count<len(list_of_authors):
                list_of_authors_in_paper += " and "
        paper_record["authors"] = list_of_authors_in_paper

        
#        if "affiliations" in paper_item.keys():
#            new_institution = models.Institution()
#            new_institution.name = paper_item["affiliations"]
#            new_institution.save()
#
#            if list_of_authors_in_paper:
#                for author_item in list_of_authors_in_paper:
#                    new_affiliation = models.Affiliation()
#                    new_affiliation.institution = new_institution
#                    new_affiliation.author = author_item
#                    new_affiliation.year = new_paper_entry.paper_year
#                    new_affiliation.save()

    models.Paper.objects.bulk_create(paper_models)
    models.Journal.objects.bulk_create(journal_models)
    models.Author.objects.bulk_create(author_models)
    print(paper_count, journal_count, all_author_list)
    return



#def insert_articles_from_web(collection_of_articles):
#    """
#    Insert a dictionary of publications into separate database rows.
#    """
#
#    for paper_item in collection_of_articles:
#        list_of_authors = paper_item["authors"].split(";")
#        list_of_authors_in_paper = []
#        for author_entry in list_of_authors:
#            author_entry = author_entry.strip()
#            new_author_item = Author()
#            new_author_item.full_name = author_entry
#            new_author_item.save()
#            list_of_authors_in_paper.append(new_author_item)
#
#        if "pubtitle" in paper_item.keys():
#            new_journal_entry = Journal()
#            new_journal_entry.name = paper_item["pubtitle"]
#            if "publisher" in paper_item.keys():
#                new_journal_entry.organization = paper_item["publisher"]
#            if "issn" in paper_item.keys():
#                new_journal_entry.issn_number = paper_item["issn"]
#            if "pubtype" in paper_item.keys():
#                new_journal_entry.pub_type = paper_item["pubtype"]
#            new_journal_entry.save()
#
#        new_paper_entry = Paper()
#        new_paper_entry.paper_title = paper_item["title"]
#        new_paper_entry.paper_journal = new_journal_entry
#        new_paper_entry.save()
#        author_position = 1
#        for author_in_paper in list_of_authors_in_paper:
#            paper_contributor = Contributor(paper = new_paper_entry,
#                                            author = author_in_paper,
#                                            position = author_position)
#            author_position += 1
#            paper_contributor.save()
#            new_paper_entry.save()
#
#        if "py" in paper_item.keys():
#            new_paper_entry.paper_year = paper_item["py"]
#        if "month" in paper_item.keys():
#            new_paper_entry.paper_month = paper_item["month"]
#        if "volume" in paper_item.keys():
#            new_paper_entry.paper_volume = paper_item["volume"]
#        if "punumber" in paper_item.keys():
#            new_paper_entry.paper_number = paper_item["punumber"]
#        if "spage" in paper_item.keys():
#            new_paper_entry.paper_pages = paper_item["spage"]+"-"
#        else:
#            new_paper_entry.paper_pages = "-"
#        if "epage" in paper_item.keys():
#            new_paper_entry.paper_pages += paper_item["epage"]
#        if "abstract" in paper_item.keys():
#            new_paper_entry.paper_abstract = paper_item["abstract"]
#        if "doi" in paper_item.keys():
#            new_paper_entry.paper_doi = paper_item["doi"]
#        if "issue" in paper_item.keys():
#            new_paper_entry.paper_issue = paper_item["issue"]
#        if "term" in paper_item.keys():
#            new_paper_entry.paper_keywords = ""
#            for term_item in paper_item["term"]:
#                new_paper_entry.paper_keywords += term_item + ", "
#            new_paper_entry.paper_keywords = new_paper_entry.paper_keywords[:-2]
#        if "mdurl" in paper_item.keys():
#            new_paper_entry.paper_url = paper_item["mdurl"]
#        if "pdf" in paper_item.keys():
#            new_paper_entry.paper_pdflink = paper_item["pdf"]
#        if "publicationId" in paper_item.keys():
#            new_paper_entry.paper_arnumber = paper_item["publicationId"]
#        elif "partnum" in paper_item.keys():
#            new_paper_entry.paper_arnumber = paper_item["partnum"]
#        elif "arnumber" in paper_item.keys():
#            new_paper_entry.paper_arnumber = paper_item["arnumber"]
#        new_paper_entry.save()
#
#        if "affiliations" in paper_item.keys():
#            new_institution = models.Institution()
#            new_institution.name = paper_item["affiliations"]
#            new_institution.save()
#
#            if list_of_authors_in_paper:
#                for author_item in list_of_authors_in_paper:
#                    new_affiliation = models.Affiliation()
#                    new_affiliation.institution = new_institution
#                    new_affiliation.author = author_item
#                    new_affiliation.year = new_paper_entry.paper_year
#                    new_affiliation.save()
#        print(new_paper_entry.id)
#
#    return


def dbase_populate(request):
    """
    Extract BibTex items from a BibTex file and insert into
    the database.
    """
    collection_of_articles = backup_data.read_ref_file()
    insert_articles_into_db(collection_of_articles)
    return HttpResponse("Database written.")


def extract_xml_field(xml_line, search_items):
    for search_item in search_items:
        if xml_line[1:len(search_item)+1]==search_item:
            search_entry = xml_line
            search_entry = search_entry.split(search_item)[1]
            search_entry = search_entry.split("CDATA")[1]
            search_entry = search_entry[1:]
            search_entry = search_entry[:-5]
            return [search_item, search_entry]


def dbase_web(request):
    search_response = urllib2.urlopen(\
        'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?py=2015&issn=0885-8993&hc=1000')
    collection_of_articles = []
    start_paper = False
    search_fields = ["title", "authors", "affiliations", "pubtitle", "punumber", \
                    "pubtype", "publisher", "volume", "issue", "py", "spage", \
                    "epage", "abstract", "issn", "arnumber", "doi", "publicationId", \
                    "partnum", "mdurl", "pdf", "term"]
    for search_line in search_response:
        edit_line = search_line.strip()
        if edit_line=="<document>":
            record = {}
            start_paper = True
        elif start_paper:
            extracted_fields = extract_xml_field(edit_line, search_fields)
            if extracted_fields:
                if extracted_fields[0]=="term":
                    if extracted_fields[0] in record.keys():
                        record[extracted_fields[0]].append(extracted_fields[1])
                    else:
                        record[extracted_fields[0]] = [extracted_fields[1], ]
                else:
                    record[extracted_fields[0]] = extracted_fields[1]
            if edit_line=="</document>":
                start_paper = False
                collection_of_articles.append(record)
    
    for item in collection_of_articles:
        for paper_item in item.keys():
            print(paper_item, item[paper_item])
        print
        print

    insert_articles_from_web(collection_of_articles)

    return HttpResponse("Database written")


class BaseView(View):

    def get_context_data(self, *args, **kwargs):
        self.context = {}

    def get(self, request, *args, **kwargs):
        self.get_context_data(request)
        return render(request, \
                    self.template_name, \
                    self.context) #, \
#                    context_instance = RequestContext(request))

    def post(self, request, *args, **kwargs):
        self.get_context_data(request)
        return render(request, \
                    self.template_name, \
                    self.context) #, \
#                    context_instance = RequestContext(request))


class PaperAuthors:
    def get_author_data(self, *args, **kwargs):
        article_authors = []
        if "paper_item" in kwargs:
            paper_item = kwargs["paper_item"]
            authors_in_paper = Contributor.objects.filter(paper = paper_item).order_by('position')
            article_authors = [author_item.author for author_item in authors_in_paper]
#            authors_in_paper = paper_item.paper_authors.all()
#            author_position = 1
#            while author_position <= len(authors_in_paper):
#                for authors in authors_in_paper:
#                    author_contrib = Contributor.objects.get(paper = paper_item,
#                                                             author = authors)
#                    if author_position == author_contrib.position:
#                        article_authors.append(authors)
#                        author_position += 1
#                        break
        return article_authors

    def extract_author_forms(self, request, *args, **kwargs):
        """
        Extracts author information from an author form
        created out of an AuthorForm ModelForm.
        """
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

    def save_author_data(self, *args, **kwargs):
        """
        Will save the author data extracted from a request and
        insert it into the author object model.
        """
        if "author_objects" in kwargs and "author_form_data" in kwargs:
            author_objects = kwargs["author_objects"]
            author_form_data = kwargs["author_form_data"]
            for author_index in range(len(author_objects)):
                author = author_objects[author_index]
#                if author_form_data[0][author_index]:
                author.full_name = author_form_data[0][author_index]
#                if author_form_data[1][author_index]:
                author.first_name = author_form_data[1][author_index]
#                if author_form_data[2][author_index]:
                author.last_name = author_form_data[2][author_index]
#                if author_form_data[3][author_index]:
                author.middle_name = author_form_data[3][author_index]
#                if author_form_data[4][author_index]:
                author.email = author_form_data[4][author_index]
                author.save()
        return

class PapersDisplay(BaseView, PaperAuthors):
    template_name = "list_papers.html"

    def get_context_data(self, request, *args, **kwargs):
        super(PapersDisplay, self).get_context_data(request, *args, **kwargs)
#        all_articles = Paper.objects.all()
        all_articles = Paper.objects.raw('SELECT * from papercollection_paper')
        collection_of_articles = []
        for paper in all_articles:
            paper_item = []
            paper_item.append(paper)
            article_authors = self.get_author_data(paper_item=paper)
            paper_item.append(article_authors)
            collection_of_articles.append(paper_item)
        self.context['collection_of_articles'] = collection_of_articles


class EditPaper(PapersDisplay):
    template_name = "edit_paper.html"

    def save_paper_data(self, paper_object, paper_form_data):
        """
        Will save the cleaned data in a paper form into
        the paper model object.
        """
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
    
    def update_paper_form(self, request, *args, **kwargs):
        # If edit_paper is not in request.POST it means the
        # form is updated which means that data in forms needs
        # to be extracted to make sure user entered data is not
        # lost before Submit button is pressed.
        if "paper_item" in kwargs and "paper_authors" in kwargs:
            paper_item = kwargs["paper_item"]
            paper_authors = kwargs["paper_authors"]
            paper_submitted = PaperForm(request.POST)
            if paper_submitted.is_valid():
                paper_received = paper_submitted.cleaned_data
                self.save_paper_data(paper_item, paper_received)

            author_form_data = self.extract_author_forms(request)
            self.save_author_data(author_objects=paper_authors, \
                                author_form_data=author_form_data)

            journal_submitted = JournalForm(request.POST)
            if journal_submitted.is_valid():
                journal_received = journal_submitted.cleaned_data
                paper_item.paper_journal.name = journal_received["name"]
                if journal_received["organization"]:
                    paper_item.paper_journal.organization = \
                            journal_received["organization"]
                paper_item.paper_journal.save()
                paper_item.save()
        return

    def get_context_data(self, request, *args, **kwargs):
        super(EditPaper, self).get_context_data(request, *args, **kwargs)
        if not request.method == "POST":
            self.template_name = "browse_choices.html"
            self.context = {}
        else:
            if "paper_srno" in request.POST:
                paper_srno = int(request.POST["paper_srno"])
            # Retrieve the edited paper from database
            edit_paper = Paper.objects.get(id = paper_srno)
            author_list = self.get_author_data(paper_item=edit_paper)

            # If the user presses the Submit button, the original paper
            # is destroyed and also any contributor objects with this
            # paper.
            if "paper_submit" in request.POST and request.POST["paper_submit"]=="Submit paper":
                self.update_paper_form(request, \
                                paper_item=edit_paper, \
                                paper_authors = author_list)
                super(EditPaper, self).get_context_data(request, *args, **kwargs)
                self.template_name = "list_papers.html"

            # If cancel button is pressed, all the paper copies and new
            # Contributor objects with this new paper will be deleted.
            elif "cancel_edit" in request.POST and request.POST["cancel_edit"]=="Cancel":
                self.template_name = "list_papers.html"

            else:
                # Create the forms
                edit_paper_form = PaperForm(instance = edit_paper)
                author_form_list = []
                for author in author_list:
                    author_form_entry = AuthorForm(instance = author)
                    # For an author form, there are four items
                    # 1 - the form
                    # 2 - a list of other authors with the same last name
                    # 3 - the author object
                    # 4 - If the user chooses to check out another author
                    # the author info and 5 papers will be listed.
                    author_form_list.append([author_form_entry,])
                journal_form = JournalForm(instance = edit_paper.paper_journal)

                self.context['paper_id'] = paper_srno
                self.context['paper'] = edit_paper_form
                self.context['authors'] = author_form_list
                self.context['journal'] = journal_form


class AuthorsDisplay(BaseView):
    template_name = "list_authors.html"

    def get_context_data(self, request, **kwargs):
        all_authors = Author.objects.all()
        self.context = {'all_authors' : all_authors,}


class EditAuthor(AuthorsDisplay, PaperAuthors):
    template_name = "edit_author.html"

    def get_context_data(self, request, *args, **kwargs):
        super(EditAuthor, self).get_context_data(kwargs)
        if not request.method == "POST":
            self.template_name = "list_authors.html"
        else:
            if "back" in request.POST and request.POST["back"]=="Go back":
                super(EditAuthor, self).get_context_data(kwargs)
                self.template_name = "list_authors.html"
            elif "author_id" in request.POST:
                author_id = int(request.POST["author_id"])
                author_item = Author.objects.get(id=author_id)

                if "update_author" in request.POST and \
                            request.POST["update_author"]=="Update author data":
                    author_form_data = self.extract_author_forms(request)
                    self.save_author_data(author_objects=[author_item,], \
                                        author_form_data=author_form_data)

                for request_keys in request.POST:
                    if request_keys.split("_")[0]=="replaceauthor":
                        replace_author_id = int(request_keys.split("_")[-1])
                        replace_author_item = Author.objects.get(id=replace_author_id)
                        replaced_author_papers = replace_author_item.paper_set.all()
                        for replace_paper_item in replaced_author_papers:
                            old_contribution = Contributor.objects.get(paper = replace_paper_item,
                                                                       author = replace_author_item)
                            new_contribution = Contributor(paper = replace_paper_item,
                                                           author = author_item,
                                                           position = old_contribution.position)
                            new_contribution.save()
                            replace_paper_item.save()
                            old_contribution.delete()

                    if request_keys.split("_")[0]=="deleteauthor":
                        delete_author_id = int(request_keys.split("_")[-1])
                        delete_author_item = Author.objects.get(id=delete_author_id)
                        delete_author_item.delete()

                author_form = AuthorForm(instance=author_item)
                author_papers = author_item.paper_set.all()
                author_paper_list = []
                for paper_item in author_papers:
                    author_list = self.get_author_data(paper_item=paper_item)
                    author_paper_list.append([paper_item, author_list])

                other_authors = []
                other_author_papers = []
                for request_keys in request.POST:
                    if request_keys.split("_")[0]=="otherauthorchoice":
                        other_author_id = int(request_keys.split("_")[-1])
                        other_author_item = Author.objects.get(id=other_author_id)
                        other_authors.append([other_author_item, 1])
                        for other_paper_item in other_author_item.paper_set.all():
                            other_author_list = self.get_author_data(\
                                            paper_item=other_paper_item)
                            other_author_papers.append(\
                                    [other_paper_item, other_author_list])

                if not other_authors:
                    for other_author_item in Author.objects.all():
                        if not other_author_item.id == author_item.id:
                            if author_item.full_name and other_author_item.full_name:
                                if author_item.full_name.split()[-1] == \
                                            other_author_item.full_name.split()[-1]:
                                    other_authors.append([other_author_item, 0])

                self.context["author_id"] = author_id
                self.context["authors"] = author_form
                self.context["papers"] = author_paper_list
                self.context["journal"] = []
                self.context["other_authors"] = other_authors
                self.context["other_author_papers"] = other_author_papers


def new_paper(request):
    if not request.POST:
        return render(request, "new_paper.html")
    else:
        if "paperbibtex" in request.POST:
            print(request.POST)
            bibtex_item = request.POST["paperbibtex"].split("\n")
            collection_of_articles = backup_data.extract_bibtex_entries(bibtex_item)
            insert_articles_into_db(collection_of_articles)
    return HttpResponseRedirect("/display-db/")


def authors_display(request):
    author_list = Author.objects.all()
    return render(request, "list_authors.html", {'author_list' : author_list})
