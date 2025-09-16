from rest_framework import serializers
from .models import Offer, Lead, LeadScore


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'name', 'value_props', 'ideal_use_cases', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_value_props(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("value_props must be a list")
        return value
    
    def validate_ideal_use_cases(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("ideal_use_cases must be a list")
        return value


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name', 'role', 'company', 'industry', 'location', 
                 'linkedin_bio', 'upload_batch', 'created_at']
        read_only_fields = ['id', 'created_at']


class LeadScoreSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    lead_role = serializers.CharField(source='lead.role', read_only=True)
    lead_company = serializers.CharField(source='lead.company', read_only=True)
    rule_score = serializers.ReadOnlyField()
    
    class Meta:
        model = LeadScore
        fields = [
            'id', 'lead_name', 'lead_role', 'lead_company',
            'role_score', 'industry_score', 'completeness_score',
            'rule_score', 'ai_score', 'ai_intent', 'ai_reasoning', 
            'total_score', 'intent_label', 'created_at'
        ]
        read_only_fields = ['id', 'total_score', 'intent_label', 'created_at']


class LeadResultSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='lead.name')
    role = serializers.CharField(source='lead.role')
    company = serializers.CharField(source='lead.company')
    intent = serializers.CharField(source='intent_label')
    score = serializers.IntegerField(source='total_score')
    reasoning = serializers.SerializerMethodField()
    
    class Meta:
        model = LeadScore
        fields = ['name', 'role', 'company', 'intent', 'score', 'reasoning']
    
    def get_reasoning(self, obj):
        rule_reasoning = []
        
        if obj.role_score > 0:
            if obj.role_score == 20:
                rule_reasoning.append("decision maker role")
            elif obj.role_score == 10:
                rule_reasoning.append("influencer role")
        
        if obj.industry_score > 0:
            if obj.industry_score == 20:
                rule_reasoning.append("exact ICP match")
            elif obj.industry_score == 10:
                rule_reasoning.append("adjacent industry")
        
        if obj.completeness_score > 0:
            rule_reasoning.append("complete data profile")
        
        rule_part = ", ".join(rule_reasoning)
        if rule_part and obj.ai_reasoning:
            return f"Fits {rule_part}. {obj.ai_reasoning}"
        elif rule_part:
            return f"Fits {rule_part}."
        else:
            return obj.ai_reasoning or "Basic scoring applied."


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV file")
        
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        return value


class ScoreRequestSerializer(serializers.Serializer):
    offer_id = serializers.IntegerField()
    batch_id = serializers.CharField(max_length=100, required=False)
    
    def validate_offer_id(self, value):
        try:
            Offer.objects.get(id=value)
        except Offer.DoesNotExist:
            raise serializers.ValidationError("Offer with this ID does not exist")
        return value