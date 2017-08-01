from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponse,  HttpResponseRedirect
import backup_data
import models
import urllib2
from django.db import connection


def index(request):
    return render(request, "index.html")


def dbase_display(request):
    return render(request, "browse_choices.html")


#def insert_articles_into_db(collection_of_articles):
#    """
#    Insert a dictionary of publications into separate database rows.
#    """
#    
#    for paper_item in collection_of_articles:
#        list_of_authors = paper_item["author"].split(" and ")
#        list_of_authors_in_paper = []
#        for author_entry in list_of_authors:
#            while author_entry[0]==" ":
#                author_entry = author_entry[1:]
#            while author_entry[-1]==" ":
#                author_entry = author_entry[:-1]
#            new_author_item = models.Author()
#            new_author_item.full_name = author_entry
#            new_author_item.save()
#            list_of_authors_in_paper.append(new_author_item)
#
#        if "journal" in paper_item.keys():
#            new_journal_entry = models.Journal()
#            new_journal_entry.name = paper_item["journal"]
#            new_journal_entry.save()
#        if "booktitle" in paper_item.keys():
#            new_journal_entry = models.Journal()
#            new_journal_entry.name = paper_item["booktitle"]
#            new_journal_entry.save()
#
#        new_paper_entry = models.Paper()
#        new_paper_entry.paper_title = paper_item["title"]
#        new_paper_entry.paper_journal = new_journal_entry
#        new_paper_entry.save()
#        author_position = 1
#        for author_in_paper in list_of_authors_in_paper:
#            paper_contributor = models.Contributor(paper = new_paper_entry,
#                                            author = author_in_paper,
#                                            position = author_position)
#            author_position += 1
#            paper_contributor.save()
#            new_paper_entry.save()
#
#        if "year" in paper_item.keys():
#            new_paper_entry.paper_year = paper_item["year"]
#        if "month" in paper_item.keys():
#            new_paper_entry.paper_month = paper_item["month"]
#        if "volume" in paper_item.keys():
#            new_paper_entry.paper_volume = paper_item["volume"]
#        if "number" in paper_item.keys():
#            new_paper_entry.paper_number = paper_item["number"]
#        if "pages" in paper_item.keys():
#            new_paper_entry.paper_pages = paper_item["pages"]
#        if "year" in paper_item.keys():
#            new_paper_entry.paper_year = paper_item["year"]
#        if "abstract" in paper_item.keys():
#            new_paper_entry.paper_abstract = paper_item["abstract"]
#        if "doi" in paper_item.keys():
#            new_paper_entry.paper_doi = paper_item["doi"]
#        if "keywords" in paper_item.keys():
#            new_paper_entry.paper_keywords = paper_item["keywords"]
#
#        new_paper_entry.save()
#        print(new_paper_entry.id)
#
#    return


def insert_articles_into_db(collection_of_articles):
    """
    Insert a dictionary of publications into separate database rows
    from a BibTex file.
    """

    paper_search_fields = ["title", "author", "year", "month", "volume",\
                            "number", "pages", "abstract", "doi", "keywords",]
    # Collection of all the models that
    # will be written in bulk
    paper_models = []
    author_models = []
    journal_models = []
    journal_list = []
    for paper_item in collection_of_articles:
        paper_record = {}
        author_record = {}
        keys_in_paper_item = paper_item.keys()
        for search_item in paper_search_fields:
            # There are some fields that are ambiguous.
            # These are dealt later.
            if not (search_item=="journal" or \
                    search_item=="booktitle"
                    ):
                if search_item in keys_in_paper_item:
                    paper_record[search_item] = paper_item[search_item]
                else:
                    paper_record[search_item] = ""

        if "journal" in keys_in_paper_item:
            paper_record["journal"] = paper_item["journal"]
        if "booktitle" in keys_in_paper_item:
            paper_record["journal"] = paper_item["booktitle"]

        paper_record["authors"] = paper_item["author"]
        list_of_authors = paper_item["author"].split(" and ")
        for author_entry in list_of_authors:
            author_entry = author_entry.strip()
            author_record["full_name"] = author_entry
            # The model is created but not witten to the database.
            author_model_item = models.Author(full_name=author_record["full_name"])
            author_models.append(author_model_item)

        if paper_record["journal"] not in journal_list:
            journal_model_item = models.Journal(name=paper_record["journal"],)
            journal_models.append(journal_model_item)
            journal_list.append(paper_record["journal"])

        paper_model_item = models.Paper(paper_title=paper_record["title"], \
                                        paper_year=paper_record["year"], \
                                        paper_volume=paper_record["volume"], \
                                        paper_issue=paper_record["number"], \
                                        paper_pages=paper_record["pages"], \
                                        paper_month=paper_record["month"], \
                                        paper_doi=paper_record["doi"], \
                                        paper_abstract=paper_record["abstract"], \
                                        paper_keywords=paper_record["keywords"], \
                                        paper_authors=paper_record["authors"], \
                                        paper_journal=paper_record["journal"]
                                    )
        paper_models.append(paper_model_item)

    # The models are written in bulk
    models.Paper.objects.bulk_create(paper_models)
    models.Journal.objects.bulk_create(journal_models)
    models.Author.objects.bulk_create(author_models)

    return


def insert_articles_from_web(collection_of_articles):
    """
    Insert a dictionary of publications into separate database rows
    from the IEEE gateway.
    """

    paper_search_fields = ["title", "authors", "affiliations", "pubtitle", "punumber", \
                    "pubtype", "publisher", "volume", "issue", "py", "spage", \
                    "epage", "abstract", "issn", "arnumber", "doi", "publicationId", \
                    "partnum", "mdurl", "pdf", "term", "month"]
    journal_search_fields = ["pubtitle", "pubtype", "publisher","issn"]
    
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
            # Some fields are different from the database.
            # These are dealt with below.
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

        # Authors are separated by ; but need to be separated by and
        list_of_authors = paper_item["authors"].split(";")
        list_of_authors_in_paper = ""
        for count, author_entry in enumerate(list_of_authors):
            author_entry = author_entry.strip()
            author_record["full_name"] = author_entry
            all_author_list.append(author_record)
            author_model_item = models.Author(full_name=author_record["full_name"])
            author_models.append(author_model_item)
            list_of_authors_in_paper += author_entry
            if count<len(list_of_authors)-1:
                list_of_authors_in_paper += " and "
        paper_record["authors"] = list_of_authors_in_paper

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

        journal_model_item = models.Journal(name=paper_record["pubtitle"], \
                                            organization=paper_record["publisher"], \
                                            issn_number=paper_record["issn"], \
                                            pub_type=paper_record["pubtype"]
                            )
        journal_models.append(journal_model_item)
        all_journal_list.append(journal_record)

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
    return


def dbase_populate(request):
    """
    Extract BibTex items from a BibTex file and insert into
    the database.
    """
    collection_of_articles = backup_data.read_ref_file()
    insert_articles_into_db(collection_of_articles)
    return HttpResponse("Database written.")


def extract_xml_field(xml_line, search_items):
    """
    Extracts the XML file received from the IEEE gateway
    """
    for search_item in search_items:
        if xml_line[1:len(search_item)+1]==search_item:
            search_entry = xml_line
            search_entry = search_entry.split(search_item)[1]
            search_entry = search_entry.split("CDATA")[1]
            search_entry = search_entry[1:]
            search_entry = search_entry[:-5]
            return [search_item, search_entry]


def dbase_web(request):
    """
    Access the IEEE gateway with th urllib2 function
    and read the XML file.
    """
    search_response = urllib2.urlopen(\
        'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?py=2014&issn=0885-8993')
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

    # Write to the database
    insert_articles_from_web(collection_of_articles)

    return HttpResponse("Database written")


class BaseView(View):

    def get_context_data(self, *args, **kwargs):
        self.context = {}

    def get(self, request, *args, **kwargs):
        self.get_context_data(request)
        return render(request, \
                    self.template_name, \
                    self.context) # , \
#                    context_instance = RequestContext(request))

    def post(self, request, *args, **kwargs):
        self.get_context_data(request)
        return render(request, \
                    self.template_name, \
                    self.context) # , \
#                    context_instance = RequestContext(request))


class PaperAuthors:
    def get_author_data(self, *args, **kwargs):
        article_authors = []
        if "paper_item" in kwargs:
            paper_item = kwargs["paper_item"]
            authors_in_paper = models.Contributor.objects.filter(paper = paper_item).\
                                order_by('position')
            article_authors = [author_item.author for author_item in authors_in_paper]
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
        all_articles = models.Paper.objects.all()
#        all_articles = models.Paper.objects.raw('SELECT * from papercollection_paper')
        collection_of_articles = []
        for paper in all_articles:
            collection_of_articles.append(paper)
        self.context['collection_of_articles'] = collection_of_articles


class EditPaper(PapersDisplay):
    template_name = "edit_paper.html"

    def save_paper_data(self, paper_object, paper_form_data):
        """
        Will save the cleaned data in a paper form into
        the paper model object.
        """
        paper_object.paper_title = paper_form_data["paper_title"]
        paper_object.paper_authors = paper_form_data["paper_authors"]
        paper_object.paper_journal = paper_form_data["paper_journal"]
        paper_object.paper_volume = paper_form_data["paper_volume"]
        paper_object.paper_issue = paper_form_data["paper_issue"]
        paper_object.paper_number = paper_form_data["paper_number"]
        paper_object.paper_pages = paper_form_data["paper_pages"]
        paper_object.paper_month = paper_form_data["paper_month"]
        paper_object.paper_year = paper_form_data["paper_year"]
        paper_object.paper_doi = paper_form_data["paper_doi"]
        paper_object.paper_keywords = paper_form_data["paper_keywords"]
        paper_object.paper_abstract = paper_form_data["paper_abstract"]
        paper_object.paper_url = paper_form_data["paper_url"]
        paper_object.paper_pdflink = paper_form_data["paper_pdflink"]
        paper_object.save()
        return
    
    def update_paper_form(self, request, *args, **kwargs):
        # If edit_paper is not in request.POST it means the
        # form is updated which means that data in forms needs
        # to be extracted to make sure user entered data is not
        # lost before Submit button is pressed.
        if "paper_item" in kwargs:
            paper_item = kwargs["paper_item"]
            paper_submitted = models.PaperForm(request.POST)
            if paper_submitted.is_valid():
                paper_received = paper_submitted.cleaned_data
                self.save_paper_data(paper_item, paper_received)

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
            edit_paper = models.Paper.objects.get(id = paper_srno)

            # If the user presses the Submit button, the original paper
            # is destroyed and also any contributor objects with this
            # paper.
            if "paper_submit" in request.POST and request.POST["paper_submit"]=="Submit paper":
                self.update_paper_form(request, \
                                paper_item=edit_paper)
                super(EditPaper, self).get_context_data(request, *args, **kwargs)
                self.template_name = "list_papers.html"

            # If cancel button is pressed, all the paper copies and new
            # Contributor objects with this new paper will be deleted.
            elif "cancel_edit" in request.POST and request.POST["cancel_edit"]=="Cancel":
                self.template_name = "list_papers.html"

            else:
                # Create the forms
                edit_paper_form = models.PaperForm(instance = edit_paper)

                self.context['paper_id'] = paper_srno
                self.context['paper'] = edit_paper_form


class AuthorsDisplay(BaseView):
    template_name = "list_authors.html"

    def get_context_data(self, request, **kwargs):
        all_authors = models.Author.objects.all()
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
                author_item = models.Author.objects.get(id=author_id)

                if "update_author" in request.POST and \
                            request.POST["update_author"]=="Update author data":
                    author_form_data = self.extract_author_forms(request)
                    self.save_author_data(author_objects=[author_item,], \
                                        author_form_data=author_form_data)

                author_form = models.AuthorForm(instance=author_item)
                author_paper_list = author_item.paper.all()
                author_last_name = author_item.full_name.split()[-1]
                free_papers = models.Paper.objects.all().\
                        filter(paper_authors__contains=author_last_name)
                for author_paper_list_item in author_paper_list:
                    free_papers = free_papers.exclude(id=author_paper_list_item.id)
                
                author_matches_in_paper = []
                chosen_paper = []
                for request_keys in request.POST:
                    if request_keys.split("_")[0]=="addpaper":
                        chosen_paper_id = int(request_keys.split("_")[-1])
                        chosen_paper = models.Paper.objects.get(id=chosen_paper_id)
                        authors_chosen_paper = chosen_paper.paper_authors.split(" and ")
                        for count, author_items in enumerate(authors_chosen_paper):
                            if author_items.split()[-1]==author_last_name:
                                author_matches_in_paper.append([author_items, count+1])

                    if request_keys.split("_")[0]=="chooseauthor":
                        confirmed_author_position = int(request_keys.split("_")[1])
                        confirmed_paper_id = int(request_keys.split("_")[2])
                        confirmed_paper = models.Paper.objects.get(id=confirmed_paper_id)
                        new_contrib = models.Contributor(author=author_item,
                                                        paper=confirmed_paper,
                                                        position=confirmed_author_position
                                                        )
                        new_contrib.save()
                        free_papers = free_papers.exclude(id=confirmed_paper_id)
                        author_paper_list = author_item.paper.all()

                self.context["author_id"] = author_id
                self.context["authors"] = author_form
                self.context["papers"] = author_paper_list
                self.context["select_papers"] = free_papers
                self.context["journal"] = []
                self.context["other_paper"] = chosen_paper
                self.context["other_paper_authors"] = author_matches_in_paper


class JournalsDisplay(BaseView):
    template_name = "list_journals.html"

    def get_context_data(self, request, *args, **kwargs):
        all_journals = models.Journal.objects.all()
        self.context = {'all_journals' : all_journals,}


def new_paper(request):
    if not request.POST:
        return render(request, "new_paper.html")
    else:
        if "paperbibtex" in request.POST:
            bibtex_item = request.POST["paperbibtex"].split("\n")
            collection_of_articles = backup_data.extract_bibtex_entries(bibtex_item)
            insert_articles_into_db(collection_of_articles)
    return HttpResponseRedirect("/display-db/")


def authors_display(request):
    author_list = models.Author.objects.all()
    return render(request, "list_authors.html", {'author_list' : author_list})
