from rest_framework.test import APITestCase

from .model_factories import *
from .serializers import *


class OrganismSerializerTest(APITestCase):
    organism = None
    serializer = None

    def setUp(self):
        self.organism = OrganismFactory.create(pk=1)
        self.serializer = OrganismSerializer(instance=self.organism)

    def tearDown(self):
        Organism.objects.all().delete()

    def test_organismSerializerHasCorrectFields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['taxa_id', 'clade', 'genus', 'species']))

    def test_organismSerializerHasCorrectData(self):
        data = self.serializer.data
        self.assertEqual(data['taxa_id'], 1)
        self.assertEqual(data['genus'], self.organism.genus)

class PfamSerializerTest(APITestCase):
    pfam = None
    serializer = None

    def setUp(self):
        self.pfam = PfamFactory.create(pk='A')
        self.serializer = PfamSerializer(instance=self.pfam)

    def tearDown(self):
        Pfam.objects.all().delete()

    def test_pfamSerializerHasCorrectFields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['domain_id', 'domain_description']))

    def test_pfamSerializerHasCorrectData(self):
        data = self.serializer.data
        self.assertEqual(data['domain_id'], 'A')
        self.assertEqual(data['domain_description'], self.pfam.description)

class DomainSerializerTest(APITestCase):
    domain = None
    pfam = None
    serializer = None

    def setUp(self):
        self.pfam = PfamFactory.create(pk='A')
        self.domain = DomainFactory.create(pfam=self.pfam)
        self.serializer = DomainSerializer(instance=self.domain)

    def tearDown(self):
        Domain.objects.all().delete()
        Pfam.objects.all().delete()

    def test_domainSerializerHasCorrectFields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['pfam_id', 'description', 'start', 'stop']))

    def test_domainSerializerHasCorrectData(self):
        data = self.serializer.data
        self.assertEqual(data['description'], self.domain.description)

    def test_domainSerializerHasCorrectPfam(self):
        data = self.serializer.data
        self.assertEqual(data['pfam_id']['domain_id'], 'A')

class ProteinSerializerRetrieveTest(APITestCase):
    protein = None
    sequence = None
    domain = None
    serializer = None

    def setUp(self):
        self.protein = ProteinFactory.create(pk='A')
        self.sequence = SequenceFactory.create(protein=self.protein)
        self.domain = DomainFactory.create(protein=self.protein)

        self.serializer = ProteinSerializer(instance=self.protein)

    def tearDown(self):
        Domain.objects.all().delete()
        Sequence.objects.all().delete()
        Organism.objects.all().delete()
        Protein.objects.all().delete()

    def test_proteinSerializerHasCorrectFields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['protein_id', 'sequence', 'taxonomy', 'length', 'domains']))

    def test_proteinSerializerHasCorrectData(self):
        data = self.serializer.data
        self.assertEqual(data['protein_id'], 'A')
        self.assertEqual(data['length'], self.protein.length)

    def test_proteinSerializerHasCorrectSequence(self):
        data = self.serializer.data
        self.assertEqual(data['sequence'], self.sequence.sequence)

    def test_proteinSerializerHasCorrectOrganism(self):
        data = self.serializer.data
        self.assertEqual(data['taxonomy']['taxa_id'], self.protein.organism.taxa_id)

    def test_proteinSerializerHasCorrectDomains(self):
        data = self.serializer.data
        self.assertEqual(data['domains'][0]['pfam_id']['domain_id'], self.domain.pfam.pfam_id)

class ProteinSerializerValidateTest(APITestCase):
    def test_proteinSerializerValidData(self):
        data = ProteinSerializerFactory.build()
        serializer = ProteinSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_proteinSerializerInvalidSequence(self):
        data = ProteinSerializerFactory.build(sequence='ABC', length=3)
        serializer = ProteinSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('sequence', serializer.errors)

    def test_proteinSerializerInvalidLength(self):
        data = ProteinSerializerFactory.build(sequence='AC', length=3)
        serializer = ProteinSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('length', serializer.errors)

    def test_proteinSerializerInvalidDomain(self):
        data = ProteinSerializerFactory.build()
        data['domains'] = [{'start': 20, 'stop': 10}]
        serializer = ProteinSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('domains', serializer.errors)

class ProteinSerializerCreateTest(APITestCase):
    data = None

    def setUp(self):
        self.data = ProteinSerializerFactory.build()
        PfamFactory.create(pk=self.data['domains'][0]['pfam_id']['domain_id'])
        OrganismFactory.create(pk=self.data['organism']['taxa_id'])

        serializer = ProteinSerializer(data=self.data)
        serializer.is_valid()
        serializer.save()

    def tearDown(self):
        Domain.objects.all().delete()
        Sequence.objects.all().delete()
        Organism.objects.all().delete()
        Protein.objects.all().delete()

    def test_proteinSerializerBasicSave(self):
        protein = Protein.objects.get(pk=self.data['protein_id'])
        self.assertEqual(self.data['protein_id'], protein.protein_id)
        self.assertEqual(self.data['length'], protein.length)

    def test_proteinSerializerSaveSequence(self):
        sequence = Sequence.objects.get(pk=self.data['protein_id'])
        self.assertEqual(self.data['sequence'], sequence.sequence)

    def test_proteinSerializerSaveOrganism(self):
        protein = Protein.objects.get(pk=self.data['protein_id'])
        organism = Organism.objects.get(pk=self.data['taxonomy']['taxa_id'])
        self.assertEqual(organism, protein.organism)

    def test_proteinSerializerSaveDomains(self):
        protein = Protein.objects.get(pk=self.data['protein_id'])
        domain = Domain.objects.filter(protein=protein)
        self.assertListEqual([protein.protein_id] * 3, [d.protein.protein_id for d in domain])
