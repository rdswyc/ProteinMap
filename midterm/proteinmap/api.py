# I wrote this code

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import *
from .serializers import *

class ProteinCreate(generics.CreateAPIView):
    """
    API view for creating a protein instance using the serializer.
    """
    queryset = Protein.objects.all()  
    serializer_class = ProteinSerializer

class ProteinDetail(generics.RetrieveAPIView):
    """
    API view for retrieving a protein instance using the serializer.
    """
    queryset = Protein.objects.all()  
    serializer_class = ProteinSerializer

class PfamDetail(generics.RetrieveAPIView):
    """
    API view for retrieving a pfam instance using the serializer.
    """
    queryset = Pfam.objects.all()  
    serializer_class = PfamSerializer

class OrganismProteins(generics.ListAPIView):
    """
    API view for listing protein instances for a given organism.
    """
    serializer_class = ProteinListSerializer

    def get_queryset(self):
        taxa = self.kwargs.get('taxa')
        return Protein.objects.filter(organism=taxa)

class OrganismPfams(generics.ListAPIView):
    """
    API view for listing pfam instances in all the proteins for a given organism.
    """
    serializer_class = DomainListSerializer

    def get_queryset(self):
        taxa = self.kwargs.get('taxa')
        return Domain.objects.filter(protein__organism=taxa)

@api_view(['GET'])
def domain_coverage(request, protein_id):
    """
    API method to return the domain coverage for a given protein.

    Rational:
        filter `Domain` by protein, then subtract the sum of stops from the sum of starts and divide by protein legth.
    """
    queryset = Domain.objects.filter(protein=protein_id)

    if not queryset.exists():
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    sums = queryset.aggregate(Sum('stop'), Sum('start'))
    length = queryset.values_list('protein__length')[0][0]
    coverage = (sums['stop__sum'] - sums['start__sum']) / length
    return Response(coverage)

# end of code I wrote