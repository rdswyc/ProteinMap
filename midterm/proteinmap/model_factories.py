# I wrote this code

from django.conf import settings
from random import choices, randint
import factory

from .models import *
from .serializers import *

class OrganismFactory(factory.django.DjangoModelFactory):
    """
    Factory for `Organism` with random `taxa_id`, 'faker' `genus` and `species`.
    """
    taxa_id = randint(1, 100000)
    clade = 'E'
    genus = factory.Faker('last_name')
    species = factory.Faker('name')

    class Meta:
        model = Organism

class ProteinFactory(factory.django.DjangoModelFactory):
    """
    Factory for `Protein` with sequence `protein_id`, random `length` and sub-factory for `organism`.
    """
    protein_id = factory.Sequence(lambda n: 'protein%d' % n)
    length = randint(1, 1000)
    organism = factory.SubFactory(OrganismFactory)

    class Meta:
        model = Protein

class SequenceFactory(factory.django.DjangoModelFactory):
    """
    Factory for `Sequence` with sub-factory for `protein`, and random `sequence` including acepted amino acid characters.
    """
    protein = factory.SubFactory(ProteinFactory)
    sequence = ''.join(choices(settings.AMINOACIDS, k=randint(1, 1000)))

    class Meta:
        model = Sequence

class PfamFactory(factory.django.DjangoModelFactory):
    """
    Factory for `Pfam` with sequence `pfam_id` and 'faker' `description`.
    """
    pfam_id = factory.Sequence(lambda n: 'pfam%d' % n)
    description = factory.Faker('sentence', nb_words=2)

    class Meta:
        model = Pfam

class DomainFactory(factory.django.DjangoModelFactory):
    """
    Factory for `Domain` with sub-factory for `protein`, `pfam`, 'faker' `description` and random `start`, `stop`.
    """
    protein = factory.SubFactory(ProteinFactory)
    pfam = factory.SubFactory(PfamFactory)
    description = factory.Faker('sentence', nb_words=2)
    start = randint(1, 500)
    stop = randint(501, 1000)

    class Meta:
        model = Domain


class ProteinSerializerFactory(factory.DictFactory):
    """
    Factory for `ProteinSerializer` data instance, used for serializer and API tests.
    """
    protein_id = ProteinFactory.build().protein_id
    sequence = SequenceFactory.build().sequence
    taxonomy = organism = {
        'taxa_id': OrganismFactory.build().taxa_id,
        'clade': OrganismFactory.build().clade,
        'genus': OrganismFactory.build().genus,
        'species': OrganismFactory.build().species
    }
    length = len(sequence)
    domains = [{
        'description': d.description,
        'start': d.start,
        'stop': d.stop,
        'pfam_id': {
            'domain_id': d.pfam.pfam_id,
            'domain_description': d.pfam.description
        }
    } for d in DomainFactory.build_batch(3)]

# end of code I wrote