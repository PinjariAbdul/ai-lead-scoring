import re
from typing import Dict, List, Tuple
from django.conf import settings
from .models import Lead, Offer, LeadScore

# Safe OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class ScoringService:
    """Service for scoring leads using rule-based logic and AI"""
    
    def __init__(self):
        self.openai_client = None
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your_openai_api_key_here':
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
    
    def score_lead(self, lead: Lead, offer: Offer) -> LeadScore:
        """Score a single lead against an offer"""
        # Calculate rule-based scores
        role_score = self._calculate_role_score(lead.role)
        industry_score = self._calculate_industry_score(lead.industry, offer.ideal_use_cases)
        completeness_score = self._calculate_completeness_score(lead)
        
        # Calculate AI score
        ai_score, ai_intent, ai_reasoning = self._calculate_ai_score(lead, offer)
        
        # Create or update lead score
        lead_score, created = LeadScore.objects.update_or_create(
            lead=lead,
            defaults={
                'offer': offer,
                'role_score': role_score,
                'industry_score': industry_score,
                'completeness_score': completeness_score,
                'ai_score': ai_score,
                'ai_intent': ai_intent,
                'ai_reasoning': ai_reasoning,
            }
        )
        
        return lead_score
    
    def _calculate_role_score(self, role: str) -> int:
        """Calculate score based on role relevance (max 20 points)"""
        if not role:
            return 0
        
        role_lower = role.lower()
        
        # Decision maker roles (20 points)
        decision_maker_keywords = [
            'ceo', 'cto', 'cfo', 'cmo', 'vp', 'vice president', 'president',
            'director', 'head of', 'chief', 'founder', 'owner', 'manager',
            'lead', 'principal', 'senior manager'
        ]
        
        # Influencer roles (10 points)
        influencer_keywords = [
            'senior', 'specialist', 'analyst', 'coordinator', 'supervisor',
            'team lead', 'project manager', 'product manager', 'marketing manager'
        ]
        
        for keyword in decision_maker_keywords:
            if keyword in role_lower:
                return 20
        
        for keyword in influencer_keywords:
            if keyword in role_lower:
                return 10
        
        return 0
    
    def _calculate_industry_score(self, industry: str, ideal_use_cases: List[str]) -> int:
        """Calculate score based on industry match (max 20 points)"""
        if not industry or not ideal_use_cases:
            return 0
        
        industry_lower = industry.lower()
        
        # Check for exact matches (20 points)
        for use_case in ideal_use_cases:
            if use_case.lower() in industry_lower or industry_lower in use_case.lower():
                return 20
        
        # Check for adjacent/related industries (10 points)
        adjacent_mappings = {
            'saas': ['software', 'technology', 'tech', 'b2b', 'enterprise'],
            'software': ['saas', 'technology', 'tech', 'it', 'digital'],
            'technology': ['software', 'saas', 'tech', 'it', 'digital'],
            'b2b': ['saas', 'enterprise', 'business', 'corporate'],
            'enterprise': ['b2b', 'corporate', 'business', 'large'],
            'mid-market': ['medium', 'middle', 'smb', 'small business'],
            'fintech': ['finance', 'financial', 'banking', 'payments'],
            'healthcare': ['medical', 'health', 'pharma', 'biotech'],
            'ecommerce': ['retail', 'commerce', 'online', 'marketplace'],
        }
        
        for use_case in ideal_use_cases:
            use_case_lower = use_case.lower()
            for key, adjacents in adjacent_mappings.items():
                if key in use_case_lower:
                    for adjacent in adjacents:
                        if adjacent in industry_lower:
                            return 10
                elif key in industry_lower:
                    for adjacent in adjacents:
                        if adjacent in use_case_lower:
                            return 10
        
        return 0
    
    def _calculate_completeness_score(self, lead: Lead) -> int:
        """Calculate score based on data completeness (max 10 points)"""
        required_fields = [lead.name, lead.role, lead.company, lead.industry, lead.location, lead.linkedin_bio]
        completed_fields = sum(1 for field in required_fields if field and field.strip())
        
        # All fields present = 10 points
        if completed_fields == len(required_fields):
            return 10
        # Most fields present = 5 points
        elif completed_fields >= 4:
            return 5
        
        return 0
    
    def _calculate_ai_score(self, lead: Lead, offer: Offer) -> Tuple[int, str, str]:
        """Calculate AI-based score (max 50 points)"""
        if not self.openai_client:
            # Enhanced fallback scoring based on rule-based analysis
            role_score = self._calculate_role_score(lead.role)
            industry_score = self._calculate_industry_score(lead.industry, offer.ideal_use_cases)
            completeness_score = self._calculate_completeness_score(lead)
            
            # Calculate fallback AI score based on rule scores
            total_rule_score = role_score + industry_score + completeness_score
            
            if total_rule_score >= 40:  # Strong rule-based fit
                ai_score = 45
                intent = 'High'
                reasoning = 'Strong profile match with decision-making role and industry alignment'
            elif total_rule_score >= 25:  # Moderate fit
                ai_score = 30
                intent = 'Medium' 
                reasoning = 'Good profile with some relevant qualifications'
            else:  # Weak fit
                ai_score = 15
                intent = 'Low'
                reasoning = 'Limited alignment with target profile'
                
            return ai_score, intent, f'{reasoning} (AI fallback scoring)'
        
        try:
            # Prepare context for AI
            lead_context = self._prepare_lead_context(lead)
            offer_context = self._prepare_offer_context(offer)
            
            prompt = f"""
You are a lead qualification expert. Analyze this prospect against the product/offer and classify their buying intent.

PRODUCT/OFFER:
{offer_context}

PROSPECT:
{lead_context}

Classify the prospect's intent as High, Medium, or Low based on:
1. Role fit (decision-making authority)
2. Industry/use case alignment
3. Profile completeness and quality
4. Likelihood to benefit from the offer

Respond with exactly this format:
INTENT: [High/Medium/Low]
REASONING: [1-2 sentences explaining your classification]
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a lead qualification expert that provides concise, actionable assessments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse response
            intent, reasoning = self._parse_ai_response(response_text)
            
            # Map intent to score
            score_mapping = {'High': 50, 'Medium': 30, 'Low': 10}
            ai_score = score_mapping.get(intent, 25)
            
            return ai_score, intent, reasoning
            
        except Exception as e:
            # Enhanced fallback with error details
            print(f"AI scoring error: {e}")
            # Use the same enhanced fallback logic
            role_score = self._calculate_role_score(lead.role)
            industry_score = self._calculate_industry_score(lead.industry, offer.ideal_use_cases)
            completeness_score = self._calculate_completeness_score(lead)
            total_rule_score = role_score + industry_score + completeness_score
            
            if total_rule_score >= 40:
                return 40, 'High', f'AI unavailable - rule-based high score ({total_rule_score}/50)'
            elif total_rule_score >= 25:
                return 25, 'Medium', f'AI unavailable - rule-based medium score ({total_rule_score}/50)'
            else:
                return 15, 'Low', f'AI unavailable - rule-based low score ({total_rule_score}/50)'
    
    def _prepare_lead_context(self, lead: Lead) -> str:
        """Prepare lead information for AI analysis"""
        context_parts = []
        
        if lead.name:
            context_parts.append(f"Name: {lead.name}")
        if lead.role:
            context_parts.append(f"Role: {lead.role}")
        if lead.company:
            context_parts.append(f"Company: {lead.company}")
        if lead.industry:
            context_parts.append(f"Industry: {lead.industry}")
        if lead.location:
            context_parts.append(f"Location: {lead.location}")
        if lead.linkedin_bio:
            # Truncate bio if too long
            bio = lead.linkedin_bio[:300] + "..." if len(lead.linkedin_bio) > 300 else lead.linkedin_bio
            context_parts.append(f"LinkedIn Bio: {bio}")
        
        return "\n".join(context_parts)
    
    def _prepare_offer_context(self, offer: Offer) -> str:
        """Prepare offer information for AI analysis"""
        context_parts = [f"Product: {offer.name}"]
        
        if offer.value_props:
            value_props = ", ".join(offer.value_props)
            context_parts.append(f"Value Propositions: {value_props}")
        
        if offer.ideal_use_cases:
            use_cases = ", ".join(offer.ideal_use_cases)
            context_parts.append(f"Ideal Use Cases: {use_cases}")
        
        return "\n".join(context_parts)
    
    def _parse_ai_response(self, response_text: str) -> Tuple[str, str]:
        """Parse AI response to extract intent and reasoning"""  # type: ignore
        intent_match = re.search(r'INTENT:\\s*(High|Medium|Low)', response_text, re.IGNORECASE)
        reasoning_match = re.search(r'REASONING:\\s*(.+)', response_text, re.IGNORECASE | re.DOTALL)
        
        intent = intent_match.group(1).title() if intent_match else 'Medium'
        reasoning = reasoning_match.group(1).strip() if reasoning_match else 'AI analysis completed'
        
        # Clean up reasoning
        reasoning = re.sub(r'\s+', ' ', reasoning)  # Clean whitespace
        reasoning = reasoning[:200]  # Limit length
        
        return intent, reasoning
    
    def score_batch(self, batch_id: str, offer: Offer) -> List[LeadScore]:
        """Score all leads in a batch"""
        leads = Lead.objects.filter(upload_batch=batch_id)
        scored_leads = []
        
        for lead in leads:
            try:
                score = self.score_lead(lead, offer)
                scored_leads.append(score)
            except Exception as e:
                # Log error but continue with other leads
                print(f"Error scoring lead {lead.id}: {str(e)}")
                continue
        
        return scored_leads