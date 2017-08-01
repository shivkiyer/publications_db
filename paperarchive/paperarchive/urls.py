"""papersarchive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from papercollection import views
import settings
import debug_toolbar


urlpatterns = [
    url(r'^debug-speed/', include(debug_toolbar.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='web-homepage'),
    url(r'^start-db/$', views.dbase_populate, name='dbase-init'),
    url(r'^ieee-db/$', views.dbase_web, name='dbase-ieee'),
    url(r'^display-db/$', views.dbase_display, name='dbase-listall'),
    url(r'^display-papers/$', views.PapersDisplay.as_view(), name='papers-listall'),
    url(r'^edit-paper/$', views.EditPaper.as_view(), name='edit-paper'),
    url(r'^display-authors/$', views.AuthorsDisplay.as_view(), name='authors-listall'),
    url(r'^edit-author/$', views.EditAuthor.as_view(), name='edit-author'),
    url(r'^display-journals/$', views.JournalsDisplay.as_view(), name='journals-listall'),
    url(r'^new-paper/$', views.new_paper, name='new-paper'),
]
