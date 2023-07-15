from django.contrib import admin

from .models import *


class OrganismAdmin(admin.ModelAdmin):
    list_display = ('taxa_id', 'clade', 'genus', 'species')

class DomainInline(admin.TabularInline):
    model = Domain
    extra = 1

class ProteinAdmin(admin.ModelAdmin):
    list_display = ('protein_id', 'length', 'organism')
    inlines = [DomainInline]

class PfamAdmin(admin.ModelAdmin):
    list_display = ('pfam_id', 'description')

class SequenceAdmin(admin.ModelAdmin):
    list_display = ('protein', 'sequence')


admin.site.register(Organism, OrganismAdmin)
admin.site.register(Protein, ProteinAdmin)
admin.site.register(Pfam, PfamAdmin)
admin.site.register(Sequence, SequenceAdmin)
