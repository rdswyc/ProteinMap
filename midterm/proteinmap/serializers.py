from rest_framework import serializers

from .models import *

class OrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = ['taxa_id', 'clade', 'genus', 'species']

class PfamSerializer(serializers.ModelSerializer):
    domain_id = serializers.CharField(source='pfam_id')
    domain_description = serializers.CharField(source='description')

    class Meta:
        model = Pfam
        fields = ['domain_id', 'domain_description']

class DomainSerializer(serializers.ModelSerializer):
    pfam_id = PfamSerializer(source='pfam')

    class Meta:
        model = Domain
        fields = ['pfam_id', 'description', 'start', 'stop']

class DomainListSerializer(serializers.ModelSerializer):
    pfam_id = PfamSerializer(source='pfam')

    class Meta:
        model = Domain
        fields = ['id', 'pfam_id']

class ProteinSerializer(serializers.ModelSerializer):
    sequence = serializers.SlugRelatedField(queryset=Sequence.objects.all(), slug_field='sequence')
    taxonomy = OrganismSerializer(source='organism')
    domains = DomainSerializer(many=True)

    class Meta:
        model = Protein
        fields = ['protein_id', 'sequence', 'taxonomy', 'length', 'domains']

class ProteinListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protein
        fields = ['protein_id']
