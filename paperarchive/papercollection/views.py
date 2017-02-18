from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,  HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import backup_data

# Create your views here.
def dbase_populate(request):
    collection_of_articles = backup_data.read_ref_file()
    return render_to_response("list_papers.html", \
                    {'collection_of_articles' : collection_of_articles}, 
                      context_instance=RequestContext(request))

def dbase_display(request):
    return HttpResponse("Hello again")
    
