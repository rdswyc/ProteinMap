import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .model_factories import *
from .serializers import *


class OrganismSerializerTest(TestCase):
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

class PfamSerializerTest(TestCase):
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

class DomainSerializerTest(TestCase):
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

class ProteinSerializerRetrieveTest(TestCase):
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

class ProteinSerializerValidateTest(TestCase):
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

class ProteinSerializerCreateTest(TestCase):
    data = None

    def setUp(self):
        self.data = ProteinSerializerFactory.build()
        PfamFactory.create(pk=self.data['domains'][0]['pfam_id']['domain_id'])
        PfamFactory.create(pk=self.data['domains'][1]['pfam_id']['domain_id'])
        PfamFactory.create(pk=self.data['domains'][2]['pfam_id']['domain_id'])
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

class ProteinCreateAPITest(APITestCase):
    url = reverse('protein_create_api')

    def tearDown(self):
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        Sequence.objects.all().delete()
        Protein.objects.all().delete()
        Pfam.objects.all().delete()

    def test_proteinCreateWithValidData(self):
        data = ProteinSerializerFactory.build()
        PfamFactory.create(pk=data['domains'][0]['pfam_id']['domain_id'])
        PfamFactory.create(pk=data['domains'][1]['pfam_id']['domain_id'])
        PfamFactory.create(pk=data['domains'][2]['pfam_id']['domain_id'])
        OrganismFactory.create(pk=data['organism']['taxa_id'])

        response = self.client.post(self.url, data, format='json')
        self.assertContains(response, 'protein_id', status_code=status.HTTP_201_CREATED)

    def test_proteinCreateReturnBadRequestWithInvalidData(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertContains(response, '', status_code=status.HTTP_400_BAD_REQUEST)

class ProteinDetailApiTest(APITestCase):
    protein = None
    sequence = None
    url = None

    def setUp(self):
        self.protein = ProteinFactory.create()
        self.sequence = SequenceFactory.create(protein=self.protein)
        self.url = reverse('protein_detail_api', kwargs={'pk': self.protein.protein_id})

    def tearDown(self):
        Domain.objects.all().delete()
        Organism.objects.all().delete()
        Sequence.objects.all().delete()
        Protein.objects.all().delete()

    def test_proteinDetailReturnSuccessStatus(self):
        response = self.client.get(self.url, format='json')
        self.assertContains(response, 'protein_id', status_code=status.HTTP_200_OK)
        self.assertContains(response, 'sequence', status_code=status.HTTP_200_OK)

    def test_proteinDetailReturnCorrectContent(self):
        response = self.client.get(self.url, format='json')
        data = json.loads(response.content)
        self.assertEqual(data['protein_id'], self.protein.protein_id)
        self.assertEqual(data['length'], self.protein.length)

    def test_proteinDetailReturnCorrectRelations(self):
        response = self.client.get(self.url, format='json')
        data = json.loads(response.content)
        self.assertEqual(data['sequence'], self.sequence.sequence)
        self.assertEqual(data['taxonomy']['taxa_id'], self.protein.organism.taxa_id)

    def test_proteinDetailReturnNotFoundOnBadPk(self):
        url = reverse('protein_detail_api', kwargs={'pk': 'x'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class PfamDetailApiTest(APITestCase):
    pfam = None
    url = None

    def setUp(self):
        self.pfam = PfamFactory.create()
        self.url = reverse('pfam_detail_api', kwargs={'pk': self.pfam.pfam_id})

    def tearDown(self):
        Pfam.objects.all().delete()

    def test_pfamDetailReturnSuccessStatus(self):
        response = self.client.get(self.url, format='json')
        self.assertContains(response, 'domain_id', status_code=status.HTTP_200_OK)
        self.assertContains(response, 'domain_description', status_code=status.HTTP_200_OK)

    def test_pfamDetailReturnCorrectContent(self):
        response = self.client.get(self.url, format='json')
        data = json.loads(response.content)
        self.assertEqual(data['domain_id'], self.pfam.pfam_id)
        self.assertEqual(data['domain_description'], self.pfam.description)

    def test_pfamDetailReturnNotFoundOnBadPk(self):
        url = reverse('pfam_detail_api', kwargs={'pk': 'x'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class OrganismProteinsApiTest(APITestCase):
    proteins = None
    url = None

    def setUp(self):
        organism = OrganismFactory.create()
        self.proteins = ProteinFactory.create_batch(3, organism=organism)
        self.url = reverse('organism_proteins_api', kwargs={'taxa': organism.taxa_id})

    def tearDown(self):
        Organism.objects.all().delete()
        Protein.objects.all().delete()

    def test_organismProteinsReturnSuccessStatus(self):
        response = self.client.get(self.url, format='json')
        self.assertContains(response, 'protein_id', 3, status.HTTP_200_OK)

    def test_organismProteinsDetailReturnCorrectContent(self):
        response = self.client.get(self.url, format='json')
        data = json.loads(response.content)
        self.assertListEqual([p.protein_id for p in self.proteins], [d['protein_id'] for d in data])

    def test_organismProteinsDetailReturnEmptyOnBadTaxa(self):
        url = reverse('organism_proteins_api', kwargs={'taxa': 0})
        response = self.client.get(url, format='json')
        self.assertContains(response, '[]', 1, status.HTTP_200_OK)

class OrganismPfamsApiTest(APITestCase):
    pfams = None
    url = None

    def setUp(self):
        organism = OrganismFactory.create()
        proteins = ProteinFactory.create_batch(3, organism=organism)
        domains = DomainFactory.create_batch(3, protein=factory.Sequence(lambda n: proteins[(n-1) % 3]))
        self.pfams = [d.pfam for d in domains]
        self.url = reverse('organism_pfams_api', kwargs={'taxa': organism.taxa_id})

    def tearDown(self):
        Organism.objects.all().delete()
        Domain.objects.all().delete()
        Pfam.objects.all().delete()
        Protein.objects.all().delete()

    def test_organismPfamsReturnSuccessStatus(self):
        response = self.client.get(self.url, format='json')
        self.assertContains(response, 'pfam_id', 3, status.HTTP_200_OK)

    def test_organismPfamsDetailReturnCorrectContent(self):
        response = self.client.get(self.url, format='json')
        data = json.loads(response.content)
        self.assertListEqual([p.pfam_id for p in self.pfams], [d['pfam_id']['domain_id'] for d in data])

    def test_organismPfamsDetailReturnEmptyOnBadTaxa(self):
        url = reverse('organism_pfams_api', kwargs={'taxa': 0})
        response = self.client.get(url, format='json')
        self.assertContains(response, '[]', 1, status.HTTP_200_OK)

class DomainCoverageApiTest(APITestCase):
    def tearDown(self):
        Domain.objects.all().delete()
        Protein.objects.all().delete()

    def test_domainCoverageWithSingleDomain(self):
        protein = ProteinFactory.create(length=2)
        DomainFactory.create(protein=protein, start=5, stop=8)

        url = reverse('domain_coverage_api', kwargs={'protein_id': protein.protein_id})
        response = self.client.get(url, format='json')
        self.assertContains(response, '1.5', 1, status.HTTP_200_OK)

    def test_domainCoverageWithMultipleDomains(self):
        protein = ProteinFactory.create(length=4)
        DomainFactory.create(protein=protein, start=10, stop=20)
        DomainFactory.create(protein=protein, start=15, stop=30)
        DomainFactory.create(protein=protein, start=3, stop=17)

        url = reverse('domain_coverage_api', kwargs={'protein_id': protein.protein_id})
        response = self.client.get(url, format='json')
        self.assertContains(response, '9.75', 1, status.HTTP_200_OK)

    def test_domainCoverageReturnNotFoundOnBadProtein(self):
        url = reverse('domain_coverage_api', kwargs={'protein_id': 0})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
