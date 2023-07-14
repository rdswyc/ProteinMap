from django.db.models import Sum
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import *
from .serializers import *

class ProteinDetail(generics.RetrieveAPIView):
    queryset = Protein.objects.all()  
    serializer_class = ProteinSerializer

class PfamDetail(generics.RetrieveAPIView):
    queryset = Pfam.objects.all()  
    serializer_class = PfamSerializer

class OrganismProteins(generics.ListAPIView):
    serializer_class = ProteinListSerializer

    def get_queryset(self):
        taxa = self.kwargs.get('taxa')
        return Protein.objects.filter(organism=taxa)

class OrganismPfams(generics.ListAPIView):
    serializer_class = DomainListSerializer

    def get_queryset(self):
        taxa = self.kwargs.get('taxa')
        return Domain.objects.filter(protein__organism=taxa)

@api_view(['GET'])
def domain_coverage(request, protein_id):
    queryset = Domain.objects.filter(protein=protein_id)
    sums = queryset.aggregate(Sum('stop'), Sum('start'))
    length = queryset.values_list('protein__length')[0][0]
    coverage = (sums['stop__sum'] - sums['start__sum']) / length
    return Response(coverage)
