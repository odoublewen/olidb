from django.contrib import admin

from oliapp.models import Annotation, Accession, Gene, Oligoset, Oligo, Experiment, Job, Recipe

admin.site.register(Annotation)
admin.site.register(Accession)
admin.site.register(Gene)
admin.site.register(Oligoset)
admin.site.register(Oligo)
admin.site.register(Experiment)
admin.site.register(Job)
admin.site.register(Recipe)
