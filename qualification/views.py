import csv
import io
import uuid
from datetime import datetime
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .models import Offer, Lead, LeadScore
from .serializers import (
    OfferSerializer, LeadSerializer, LeadScoreSerializer,
    LeadResultSerializer, CSVUploadSerializer, ScoreRequestSerializer
)
from .services import ScoringService


class OfferCreateView(APIView):
    """POST /offer - Accept JSON with product/offer details"""
    
    def post(self, request):
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadsUploadView(APIView):
    """POST /leads/upload - Accept CSV file with lead data"""
    
    def post(self, request):
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = serializer.validated_data['file']
        batch_id = f"batch_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        try:
            # Read and parse CSV
            file_content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            # Validate CSV headers
            expected_headers = {'name', 'role', 'company', 'industry', 'location', 'linkedin_bio'}
            actual_headers = set(csv_reader.fieldnames or [])
            
            if not expected_headers.issubset(actual_headers):
                missing_headers = expected_headers - actual_headers
                return Response(
                    {'error': f'Missing required CSV columns: {", ".join(missing_headers)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process leads
            leads_created = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                try:
                    # Clean and validate row data
                    lead_data = {
                        'name': row.get('name', '').strip(),
                        'role': row.get('role', '').strip(),
                        'company': row.get('company', '').strip(),
                        'industry': row.get('industry', '').strip(),
                        'location': row.get('location', '').strip(),
                        'linkedin_bio': row.get('linkedin_bio', '').strip(),
                        'upload_batch': batch_id
                    }
                    
                    # Skip empty rows
                    if not any(lead_data[field] for field in ['name', 'company']):
                        continue
                    
                    # Validate required fields
                    if not lead_data['name']:
                        errors.append(f"Row {row_num}: Name is required")
                        continue
                    
                    # Create lead
                    Lead.objects.create(**lead_data)
                    leads_created += 1
                    
                    # Check upload limit
                    if leads_created >= settings.MAX_LEADS_PER_UPLOAD:
                        break
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue
            
            if leads_created == 0:
                return Response(
                    {'error': 'No valid leads found in CSV', 'details': errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response_data = {
                'message': f'Successfully uploaded {leads_created} leads',
                'batch_id': batch_id,
                'leads_created': leads_created
            }
            
            if errors:
                response_data['warnings'] = errors[:10]  # Limit error messages
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ScoreLeadsView(APIView):
    """POST /score - Run scoring on uploaded leads"""
    
    def post(self, request):
        serializer = ScoreRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        offer_id = serializer.validated_data['offer_id']
        batch_id = serializer.validated_data.get('batch_id')
        
        try:
            offer = Offer.objects.get(id=offer_id)
            
            # Determine which leads to score
            if batch_id:
                leads = Lead.objects.filter(upload_batch=batch_id)
                if not leads.exists():
                    return Response(
                        {'error': f'No leads found for batch_id: {batch_id}'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Score all leads if no batch_id provided
                leads = Lead.objects.all()
                if not leads.exists():
                    return Response(
                        {'error': 'No leads found to score'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Initialize scoring service
            scoring_service = ScoringService()
            
            # Score leads
            scored_count = 0
            errors = []
            
            for lead in leads:
                try:
                    scoring_service.score_lead(lead, offer)
                    scored_count += 1
                except Exception as e:
                    errors.append(f"Lead {lead.id} ({lead.name}): {str(e)}")
                    continue
            
            response_data = {
                'message': f'Successfully scored {scored_count} leads',
                'total_leads': leads.count(),
                'scored_leads': scored_count,
                'offer_id': offer_id
            }
            
            if batch_id:
                response_data['batch_id'] = batch_id
            
            if errors:
                response_data['errors'] = errors[:10]  # Limit error messages
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Offer.DoesNotExist:
            return Response(
                {'error': f'Offer with id {offer_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Scoring failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResultsListView(generics.ListAPIView):
    """GET /results - Return scored leads"""
    serializer_class = LeadResultSerializer
    
    def get_queryset(self):
        queryset = LeadScore.objects.select_related('lead', 'offer')
        
        # Filter by offer_id if provided
        offer_id = self.request.query_params.get('offer_id')
        if offer_id:
            queryset = queryset.filter(offer_id=offer_id)
        
        # Filter by batch_id if provided
        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            queryset = queryset.filter(lead__upload_batch=batch_id)
        
        # Filter by intent if provided
        intent = self.request.query_params.get('intent')
        if intent in ['High', 'Medium', 'Low']:
            queryset = queryset.filter(intent_label=intent)
        
        return queryset


class ExportResultsView(APIView):
    """GET /results/export - Export results as CSV"""
    
    def get(self, request):
        # Get same queryset as results
        queryset = LeadScore.objects.select_related('lead', 'offer')
        
        # Apply same filters
        offer_id = request.query_params.get('offer_id')
        if offer_id:
            queryset = queryset.filter(offer_id=offer_id)
        
        batch_id = request.query_params.get('batch_id')
        if batch_id:
            queryset = queryset.filter(lead__upload_batch=batch_id)
        
        intent = request.query_params.get('intent')
        if intent in ['High', 'Medium', 'Low']:
            queryset = queryset.filter(intent_label=intent)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="lead_scores.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Role', 'Company', 'Industry', 'Location', 
            'Intent', 'Score', 'Rule Score', 'AI Score', 'Reasoning'
        ])
        
        for score in queryset:
            # Generate reasoning like in serializer
            rule_reasoning = []
            if score.role_score == 20:
                rule_reasoning.append("decision maker role")
            elif score.role_score == 10:
                rule_reasoning.append("influencer role")
            
            if score.industry_score == 20:
                rule_reasoning.append("exact ICP match")
            elif score.industry_score == 10:
                rule_reasoning.append("adjacent industry")
            
            if score.completeness_score > 0:
                rule_reasoning.append("complete data profile")
            
            rule_part = ", ".join(rule_reasoning)
            if rule_part and score.ai_reasoning:
                reasoning = f"Fits {rule_part}. {score.ai_reasoning}"
            elif rule_part:
                reasoning = f"Fits {rule_part}."
            else:
                reasoning = score.ai_reasoning or "Basic scoring applied."
            
            writer.writerow([
                score.lead.name,
                score.lead.role,
                score.lead.company,
                score.lead.industry,
                score.lead.location,
                score.intent_label,
                score.total_score,
                score.rule_score,
                score.ai_score,
                reasoning
            ])
        
        return response


# API status and health check
@api_view(['GET'])
def api_status(request):
    """GET / - API status and health check"""
    return Response({
        'status': 'healthy',
        'service': 'Lead Qualification API',
        'version': '1.0.0',
        'endpoints': {
            'POST /offer': 'Create product/offer',
            'POST /leads/upload': 'Upload leads CSV',
            'POST /score': 'Score leads',
            'GET /results': 'Get scored results',
            'GET /results/export': 'Export results as CSV'
        }
    })
