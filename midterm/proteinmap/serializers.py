from rest_framework import serializers

from .models import *

class OrganismSerializer(serializers.ModelSerializer):
    taxa_id = serializers.IntegerField(validators=[])
    clade = serializers.CharField(read_only=True)
    genus = serializers.CharField(read_only=True)
    species = serializers.CharField(read_only=True)

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
    sequence = serializers.CharField(allow_null=True, style={'base_template': 'textarea.html'})
    taxonomy = OrganismSerializer(source='organism', style={'base_template': 'fieldset.html', 'hide_label': True})
    domains = DomainSerializer(many=True)

    class Meta:
        model = Protein
        fields = ['protein_id', 'sequence', 'taxonomy', 'length', 'domains']

    def create(self, validated_data):
        sequence = validated_data.pop('sequence')
        domains = validated_data.pop('domains')
        taxa_id = validated_data.pop('organism')['taxa_id']

        organism = Organism.objects.get(pk=taxa_id)
        protein = Protein.objects.create(organism=organism, **validated_data)

        if sequence is not None:
            Sequence.objects.create(protein=protein, sequence=sequence)

        for domain in domains:
            pfam = Pfam.objects.get(pk=domain.pop('pfam')['pfam_id'])
            Domain.objects.create(protein=protein, pfam=pfam, **domain)

        return protein

    def validate_sequence(self, value):
        if not all(a in 'ACDEFGHIKLMNPQRSTVWY' for a in value):
            raise serializers.ValidationError('Sequence contains invalid amino acids')
        return value

    def validate_length(self, value):
        if value != len(self.initial_data.get('sequence')):
            raise serializers.ValidationError('Protein length and sequence length should be the same')
        return value

    def validate_domains(self, value):
        for domain in value:
            if domain['start'] > domain['stop']:
                raise serializers.ValidationError('Domain stop must be greaten than start')
        return value

class ProteinListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protein
        fields = ['protein_id']
