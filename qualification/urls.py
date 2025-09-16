from django.urls import path
from . import views

app_name = 'qualification'

urlpatterns = [
    path('', views.api_status, name='api_status'),
    path('offer/', views.OfferCreateView.as_view(), name='offer_create'),
    path('leads/upload/', views.LeadsUploadView.as_view(), name='leads_upload'),
    path('score/', views.ScoreLeadsView.as_view(), name='score_leads'),
    path('results/', views.ResultsListView.as_view(), name='results_list'),
    path('results/export/', views.ExportResultsView.as_view(), name='results_export'),
]