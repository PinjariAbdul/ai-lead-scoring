from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Offer(models.Model):
    """Model to store product/offer information"""
    name = models.CharField(max_length=255)
    value_props = models.JSONField(help_text="List of value propositions")
    ideal_use_cases = models.JSONField(help_text="List of ideal use cases/industries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Lead(models.Model):
    """Model to store lead information"""
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    linkedin_bio = models.TextField(blank=True)
    upload_batch = models.CharField(max_length=100, help_text="Batch identifier for uploaded leads")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.company}"
    
    class Meta:
        ordering = ['-created_at']


class LeadScore(models.Model):
    """Model to store lead scoring results"""
    INTENT_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='score')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    
    # Rule-based scoring (max 50 points)
    role_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="Score based on role relevance (0-20)"
    )
    industry_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="Score based on industry match (0-20)"
    )
    completeness_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Score based on data completeness (0-10)"
    )
    
    # AI-based scoring (max 50 points)
    ai_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Score from AI analysis (0-50)"
    )
    ai_intent = models.CharField(
        max_length=10,
        choices=INTENT_CHOICES,
        help_text="AI-determined intent level"
    )
    ai_reasoning = models.TextField(
        help_text="AI explanation for the scoring"
    )
    
    # Final results
    total_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Total score (rule_score + ai_score)"
    )
    intent_label = models.CharField(
        max_length=10,
        choices=INTENT_CHOICES,
        help_text="Final intent classification"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Calculate total score
        rule_score = self.role_score + self.industry_score + self.completeness_score
        self.total_score = rule_score + self.ai_score
        
        # Determine final intent based on total score
        if self.total_score >= 70:
            self.intent_label = 'High'
        elif self.total_score >= 40:
            self.intent_label = 'Medium'
        else:
            self.intent_label = 'Low'
            
        super().save(*args, **kwargs)
    
    @property
    def rule_score(self):
        return self.role_score + self.industry_score + self.completeness_score
    
    def __str__(self):
        return f"{self.lead.name} - {self.intent_label} ({self.total_score})"
    
    class Meta:
        ordering = ['-total_score', '-created_at']
