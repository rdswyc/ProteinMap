import factory
from random import choices, randint

from django.conf import settings
from .models import *

class OrganismFactory(factory.django.DjangoModelFactory):
    taxa_id = randint(1, 100000)
    clade = 'E'
    genus = factory.Faker('last_name')
    species = factory.Faker('name')

    class Meta:
        model = Organism

class ProteinFactory(factory.django.DjangoModelFactory):
    protein_id = hex(randint(1, 100000))[2:]
    length = randint(1, 1000)
    organism = factory.SubFactory(OrganismFactory)

    class Meta:
        model = Protein

class SequenceFactory(factory.django.DjangoModelFactory):
    protein = factory.SubFactory(ProteinFactory)
    sequence = ''.join(choices(settings.AMINOACIDS, k=randint(1, 1000)))

    class Meta:
        model = Sequence

class PfamFactory(factory.django.DjangoModelFactory):
    pfam_id = hex(randint(1, 100000))[2:]
    description = factory.Faker('sentence', nb_words=2)

    class Meta:
        model = Pfam

class DomainFactory(factory.django.DjangoModelFactory):
    protein = factory.SubFactory(ProteinFactory)
    pfam = factory.SubFactory(PfamFactory)
    description = factory.Faker('sentence', nb_words=2)
    start = randint(1, 1000)
    stop = randint(1, 1000)

    class Meta:
        model = Domain
