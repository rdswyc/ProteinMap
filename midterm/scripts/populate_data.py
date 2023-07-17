# I wrote this code

import os
import sys
import django
import csv

sys.path.append('../midterm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'midterm.settings')
django.setup()

from proteinmap.models import *


"""
Populate Pfam table with pfam_descriptions file
"""

Pfam.objects.all().delete()

data_file = '../data/pfam_descriptions.csv'
with open(data_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    pfams = {}
    for row in csv_reader:
        pfams[row[0]] = Pfam(pfam_id=row[0], description=row[1])

    Pfam.objects.bulk_create(pfams.values())


"""
Populate Organisms, Protein and Domain tables with assignment_data_set file
"""

Organism.objects.all().delete()
Protein.objects.all().delete()
Domain.objects.all().delete()

data_file = '../data/assignment_data_set.csv'
with open(data_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    organisms = {}
    proteins = {}
    domains = []

    for row in csv_reader:
        genus, species = row[3].partition(' ')[0], row[3].partition(' ')[2]
        organisms[row[1]] = Organism(taxa_id=row[1], clade=row[2], genus=genus, species=species)
        proteins[row[0]] = Protein(protein_id=row[0], length=row[8], organism=organisms[row[1]])
        domains.append(Domain(description=row[4], start=row[6], stop=row[7], protein=proteins[row[0]], pfam=pfams[row[5]]))

    Organism.objects.bulk_create(organisms.values())
    Protein.objects.bulk_create(proteins.values())
    Domain.objects.bulk_create(domains)


"""
Populate ProteinSequence table with assignment_data_sequences file
"""

Sequence.objects.all().delete()

data_file = '../data/assignment_data_sequences.csv'
with open(data_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    sequences = []
    for row in csv_reader:
        sequences.append(Sequence(protein=proteins[row[0]], sequence=row[1]))

    Sequence.objects.bulk_create(sequences)

# end of code I wrote