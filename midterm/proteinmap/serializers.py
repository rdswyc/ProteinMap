# I wrote this code

from rest_framework import serializers

from django.conf import settings
from .models import *


class OrganismSerializer(serializers.ModelSerializer):
    """
    Serializer for `Organism` used by protein endpoints.
    Removes validators for `taxa_id` to allow `Protein` posting with existing `Organism`.
    All other attributes are read-only since an `Organism` instance is not created.
    """
    taxa_id = serializers.IntegerField(validators=[])
    clade = serializers.CharField(read_only=True)
    genus = serializers.CharField(read_only=True)
    species = serializers.CharField(read_only=True)

    class Meta:
        model = Organism
        fields = ['taxa_id', 'clade', 'genus', 'species']

class PfamSerializer(serializers.ModelSerializer):
    """
    Serializer for `Pfam` used by the pfam endpoint.
    Exposes two properties with different names on source model.
    """
    domain_id = serializers.CharField(source='pfam_id')
    domain_description = serializers.CharField(source='description')

    class Meta:
        model = Pfam
        fields = ['domain_id', 'domain_description']

class DomainSerializer(serializers.ModelSerializer):
    """
    Serializer for `Domain` used by protein endpoints.
    Exposes `pfam_id` as an object named `pfam` on source model.
    """
    pfam_id = PfamSerializer(source='pfam')

    class Meta:
        model = Domain
        fields = ['pfam_id', 'description', 'start', 'stop']

class DomainListSerializer(serializers.ModelSerializer):
    """
    Serializer for `Domain` used by the organism pfams endpoint.
    Exposes `pfam_id` as an object named `pfam` on source model.
    """
    pfam_id = PfamSerializer(source='pfam')

    class Meta:
        model = Domain
        fields = ['id', 'pfam_id']

class ProteinSerializer(serializers.ModelSerializer):
    """
    Serializer for `Protein` used by protein endpoints.
    Exposes `sequence` and `domains` as reverse relations using `related_name`.
    Exposes `taxonomy` as an object named `organism` on source model.
    """
    sequence = serializers.CharField(allow_null=True, style={'base_template': 'textarea.html'})
    taxonomy = OrganismSerializer(source='organism', style={'base_template': 'fieldset.html', 'hide_label': True})
    domains = DomainSerializer(many=True)

    class Meta:
        model = Protein
        fields = ['protein_id', 'sequence', 'taxonomy', 'length', 'domains']

    def create(self, validated_data):
        """
        Override the `create()` method in order to save `Protein` with `Sequence`
        and to utilize saved `Organism` and `Domain` instances.

        Rational:
            Remove related objects from data payload, then save `Sequence` and `Domains` fixing relations.
        """
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
        """Validate if `sequence` contains only allowed amino acid characters."""
        if not all(a in settings.AMINOACIDS for a in value):
            raise serializers.ValidationError('Sequence contains invalid amino acids')
        return value

    def validate_length(self, value):
        """Validate if `length` posted has the same length of posted `sequence`."""
        if value != len(self.initial_data.get('sequence')):
            raise serializers.ValidationError('Protein length and sequence length should be the same')
        return value

    def validate_domains(self, value):
        """Validate that all `domains` have correct `start` and `stop` relative values."""
        for domain in value:
            if domain['start'] > domain['stop']:
                raise serializers.ValidationError('Domain stop must be greaten than start')
        return value

class ProteinListSerializer(serializers.ModelSerializer):
    """
    Serializer for `Protein` used by the organism proteins endpoint.
    """
    class Meta:
        model = Protein
        fields = ['protein_id']

# end of code I wrote