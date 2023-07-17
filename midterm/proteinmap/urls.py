# I wrote this code

from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from rest_framework.schemas import get_schema_view


from . import api

urlpatterns = [
    # Redirect home path to the swagger endpoint
    re_path(r'^$', RedirectView.as_view(
        url='swagger-ui/',
        permanent=False
    ), name='index'),
    # Swagger endpoint using OpenAPI specification
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
    # OpenAPI specification endpoint
    path('openapi', get_schema_view(
        title="Protein map",
        description="By Rodrigo Chin",
        version="0.1.0"
    ), name='openapi-schema'),
    # REST API endpoints
    path('api/protein/', api.ProteinCreate.as_view(), name='protein_create_api'),
    path('api/protein/<str:pk>/', api.ProteinDetail.as_view(), name='protein_detail_api'),
    path('api/pfam/<str:pk>/', api.PfamDetail.as_view(), name='pfam_detail_api'),
    path('api/proteins/<str:taxa>', api.OrganismProteins.as_view(), name='organism_proteins_api'),
    path('api/pfams/<str:taxa>', api.OrganismPfams.as_view(), name='organism_pfams_api'),
    path('api/coverage/<str:protein_id>', api.domain_coverage, name='domain_coverage_api'),
]

# end of code I wrote