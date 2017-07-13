from django.views.generic import View
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,  HttpResponseRedirect
from django.template import RequestContext
import backup_data
from papercollection.models import Author, Journal, Paper, Contributor
from papercollection.models import AuthorForm, JournalForm, PaperForm


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

    return


def dbase_populate(request):
    """
    Extract BibTex items from a BibTex file and insert into
    the database.
    """
    collection_of_articles = backup_data.read_ref_file()
    insert_articles_into_db(collection_of_articles)
    return HttpResponse("Database written.")

class BaseView(View):

    def get_context_data(self, *args, **kwargs):
        self.context = {}

    def get(self, request, *args, **kwargs):
        self.get_context_data(request)
        return render(request, \
                    self.template_name, \
                    self.context, \
                    context_instance = RequestContext(request))

    def post(self, request, *args, **kwargs):
        self.get_context_data(request)
        return render(request, \
                    self.template_name, \
                    self.context, \
                    context_instance = RequestContext(request))


class PaperAuthors:
    def get_author_data(self, *args, **kwargs):
        article_authors = []
        if "paper_item" in kwargs:
            paper_item = kwargs["paper_item"]
            authors_in_paper = paper_item.paper_authors.all()
            author_position = 1
            while author_position <= len(authors_in_paper):
                for authors in authors_in_paper:
                    author_contrib = Contributor.objects.get(paper = paper_item,
                                                             author = authors)
                    if author_position == author_contrib.position:
                        article_authors.append(authors)
                        author_position += 1
                        break
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
        all_articles = Paper.objects.all()
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
