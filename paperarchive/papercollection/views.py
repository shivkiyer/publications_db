from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,  HttpResponseRedirect
from django.template import RequestContext
import backup_data
from papercollection.models import Author, Journal, Paper, Contributor
from papercollection.models import AuthorForm, JournalForm, PaperForm


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
    

def dbase_display(request):
    """
    Lists all the papers.
    """
    all_articles = Paper.objects.all()
    collection_of_articles = []
    for paper in all_articles:
        paper_item = []
        paper_item.append(paper)
        authors_in_paper = paper.paper_authors.all()
        article_authors = []
        author_position = 1
        while author_position <= len(authors_in_paper):
            for authors in authors_in_paper:
                author_contrib = Contributor.objects.get(paper = paper,
                                                         author = authors)
                if author_position == author_contrib.position:
                    article_authors.append(authors)
                    author_position += 1
                    break
        paper_item.append(article_authors)
        collection_of_articles.append(paper_item)
    return render(request, "list_papers.html", \
                    {'collection_of_articles' : collection_of_articles},
                    context_instance = RequestContext(request))


def extract_author_forms(request):
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



def save_paper_data(paper_object, paper_form_data):
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


def save_author_data(author_objects, author_form_data):
    """
    Will save the author data extracted from a request and
    insert it into the author object model.
    """
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

        author.save()

    return


def edit_paper(request):
    """
    Will create and change the form for editing a paper
    which includes the author and journal information.
    """
    if not request.method == "POST":
        return HttpResponseRedirect("/display-db/")
    else:
        if "paper_srno" in request.POST:
            paper_srno = int(request.POST["paper_srno"])
            if "edit_paper" in request.POST:
                # If edit_paper is found in request.POST, it means it is
                # the first time this function is entered. So the paper
                # initiating this will be copied and a new paper will be
                # created for the edits until the form is submitted.
                original_paper = Paper.objects.get(id = paper_srno)
                original_paper_srno = paper_srno
                edit_paper = Paper()
                edit_paper.paper_title = original_paper.paper_title
                edit_paper.paper_journal = original_paper.paper_journal
                edit_paper.save()
                edit_paper.paper_year = original_paper.paper_year
                edit_paper.paper_volume = original_paper.paper_volume
                edit_paper.paper_number = original_paper.paper_number
                edit_paper.paper_pages = original_paper.paper_pages
                edit_paper.paper_month = original_paper.paper_month
                edit_paper.paper_doi = original_paper.paper_doi
                edit_paper.paper_abstract = original_paper.paper_abstract
                edit_paper.paper_keywords = original_paper.paper_keywords
                author_list = original_paper.paper_authors.all()
                for author_in_paper in author_list:
                    author_position = author_in_paper.contributor_set.get(paper = original_paper).position
                    paper_contributor = Contributor(paper = edit_paper,
                                                    author = author_in_paper,
                                                    position = author_position)
                    paper_contributor.save()
                    edit_paper.save()

            else:
                # If edit_paper is not in request.POST, this means it
                # is an update of the form. In which case, extract the
                # original paper and the new paper and continue.
                if "original_paper_srno" in request.POST:
                    original_paper_srno = int(request.POST["original_paper_srno"])
                    original_paper = Paper.objects.get(id = original_paper_srno)
                edit_paper = Paper.objects.get(id = paper_srno)

            # Extracting the author list taking contributor positions
            # into account.
            author_list = []
            authors_in_paper = edit_paper.paper_authors.all()
            author_position = 1
            while author_position <= len(authors_in_paper):
                for author in authors_in_paper:
                    author_contrib = Contributor.objects.get(paper = edit_paper,
                                                             author = author)
                    if author_contrib.position == author_position:
                        author_list.append(author)
                        author_position += 1
                        break

            # Items for the forms that will be generated later.
            all_authors_in_db = Author.objects.all()
            journal = edit_paper.paper_journal
            # These are lists that will have options for every
            # author which means authors that have the same last name.
            list_for_author_options = []
            list_for_author_replacements = []
            for author in author_list:
                list_for_author_options.append("authorcheck_" + str(author.id))
                list_for_author_replacements.append("replaceauthor_" + str(author.id))

        # If edit_paper is not in request.POST it means the
        # form is updated which means that data in forms needs
        # to be extracted to make sure user entered data is not
        # lost before Submit button is pressed.
        if not ("edit_paper" in request.POST):
            paper_submitted = PaperForm(request.POST)
            if paper_submitted.is_valid():
                paper_received = paper_submitted.cleaned_data
                save_paper_data(edit_paper, paper_received)

            author_form_data = extract_author_forms(request)
            save_author_data(author_list, author_form_data)

            journal_submitted = JournalForm(request.POST)
            if journal_submitted.is_valid():
                journal_received = journal_submitted.cleaned_data
                journal.name = journal_received["name"]
                if journal_received["organization"]:
                    journal.organization = journal_received["organization"]
                journal.save()

        # If the user presses the Submit button, the original paper
        # is destroyed and also any contributor objects with this
        # paper.
        if "paper_submit" in request.POST and request.POST["paper_submit"]=="Submit paper":
            original_paper = Paper.objects.get(id = original_paper_srno)
            author_in_papers = original_paper.paper_authors.all()
            for author in author_in_papers:
                author_contrib = Contributor.objects.get(paper = original_paper,
                                                         author = author)
                author_contrib.delete()
            original_paper.delete()
            return HttpResponseRedirect("/display-db/")

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
            author_form_list.append([[], [], [], []])
            author_form_list[-1][0] = author_form_entry
            choices_for_author = []
            for other_authors in all_authors_in_db:
                if not other_authors.id == author.id:
                    if author.full_name and other_authors.full_name:
                        if author.full_name.split()[-1] == other_authors.full_name.split()[-1]:
                            choices_for_author.append(other_authors)
            author_form_list[-1][1] = choices_for_author
            author_form_list[-1][2] = author
        journal_form = JournalForm(instance = journal)

        # The user can check out any other authors with the same last
        # name. For that the block below will add the other author
        # object and a list of 5 papers with that author.
        for replace_author in list_for_author_options:
            if replace_author in request.POST and request.POST[replace_author]=="Check this author":
                author_srno = int(replace_author.split("_")[1])
                other_author_srno = int(request.POST["otherauthors_" + str(author_srno)])
                if not other_author_srno == -1:
                    other_author = Author.objects.get(id = other_author_srno)
                    for count1 in range(len(author_list)):
                        if author_list[count1].id == author_srno:
                            author_form_list[count1][3] = [other_author, ]
                            other_author_papers = other_author.paper_set.all()
                            if len(other_author_papers) > 5:
                                for count2 in range(len(other_author_papers)-1, 4, -1):
                                    del other_author_papers[count2]
                            author_form_list[count1][3].append(other_author_papers)

        # If the user wishes to use the other author data, this
        # block below will replace the author in this paper
        # and all other papers in which the old author entry
        # appears. The replaced author will be deleted.
        for change_author in list_for_author_replacements:
            if change_author in request.POST and request.POST[change_author]=="Use this author data":
                author_srno = int(change_author.split("_")[1])
                other_author_srno = int(request.POST["otherauthors_" + str(author_srno)])
                if not other_author_srno == -1:
                    other_author = Author.objects.get(id = other_author_srno)
                    replaced_author = Author.objects.get(id = author_srno)
                    replaced_author_papers = replaced_author.paper_set.all()
                    for paper_item in replaced_author_papers:
                        old_contribution = Contributor.objects.get(paper = paper_item,
                                                                   author = replaced_author)
                        new_contribution = Contributor(paper = paper_item,
                                                       author = other_author,
                                                       position = old_contribution.position)
                        new_contribution.save()
                        paper_item.save()
                        old_contribution.delete()

                    for author in author_list:
                        if author == replaced_author:
                            this_author_position = author_list.index(author)
                            author_form_list[this_author_position][0] = AuthorForm(instance = other_author)
                            choices_for_author = []
                            all_authors_in_db = []
                            for author_item in Author.objects.all():
                                edited_paper_authors = edit_paper.paper_authors.all()
                                original_paper_authors = original_paper.paper_authors.all()
                                if not (author_item in edited_paper_authors or \
                                        author_item in original_paper_authors):
                                    all_authors_in_db.append(author_item)

                            for other_authors in all_authors_in_db:
                                if not other_authors.id == author.id:
                                    if author.full_name and other_authors.full_name:
                                        if author.full_name.split()[-1] == other_authors.full_name.split()[-1]:
                                            choices_for_author.append(other_authors)
                            author_form_list[this_author_position][1] = choices_for_author
                            author_form_list[-1][2] = other_author
                            author_form_list[-1][3] = []
                    replaced_author.delete()


    return render(request, "edit_paper.html", \
                    {'paper_id' : paper_srno,
                    'original_paper_id' : original_paper_srno,
                    'paper' : edit_paper_form,
                    'authors' : author_form_list,
                    'journal' : journal_form
                    },
                    context_instance = RequestContext(request))



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
