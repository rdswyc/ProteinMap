from django.urls import path

from . import api

urlpatterns = [
    path('api/protein/<str:pk>/', api.ProteinDetail.as_view()),
    path('api/pfam/<str:pk>/', api.PfamDetail.as_view()),
    path('api/proteins/<str:taxa>', api.OrganismProteins.as_view()),
    path('api/pfams/<str:taxa>', api.OrganismPfams.as_view()),
    path('api/coverage/<str:protein_id>', api.domain_coverage),
]
