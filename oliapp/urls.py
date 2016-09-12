"""oliapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from oliapp import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^oligosets/$', views.browse_oligosets, name='oligosets'),

    url(r'^oligosets/detail/(?P<taxatmid>[a-z0-9/-]+)/$', views.index, name='oligoset_details'),
    url(r'^benchtop/$', views.index, name='benchtop'),
    url(r'^experiments/$', views.browse_experiments, name='experiments'),
    url(r'^search/$', views.index, name='search'),
    url(r'^design/$', views.index, name='design'),
    url(r'^results/$', views.index, name='results'),
    url(r'^login/$', views.index, name='login'),
    url(r'^logout/$', views.index, name='logout'),
]
