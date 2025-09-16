# Lead Qualification API

A Django REST Framework backend service that accepts product/offer information and CSV files of leads, then scores each lead's buying intent using rule-based logic combined with AI reasoning.

## 🎯 Overview

This API evaluates leads against products/offers and assigns intent scores (High/Medium/Low) based on:
- **Rule-based scoring** (max 50 points): Role relevance, industry match, data completeness
- **AI-powered scoring** (max 50 points): OpenAI analysis of prospect fit
- **Final classification**: High (70+), Medium (40-69), Low (<40)

## ✅ Features

- **Product/Offer Management**: Create and store product information with value propositions and ideal use cases
- **CSV Lead Upload**: Bulk upload leads with validation and batch tracking
- **Intelligent Scoring**: Rule-based + AI hybrid scoring system
- **Results API**: Retrieve scored leads with detailed reasoning
- **CSV Export**: Export results for further analysis
- **Error Handling**: Comprehensive validation and error reporting
- **Documentation**: Complete API documentation with examples

## 🚀 Live API

**🌐 Live API Base URL:** https://ai-lead-scoring.onrender.com/

### 🧪 Quick Testing

Test the API instantly in your browser or with these commands:

**Browser Test:** Visit https://ai-lead-scoring.onrender.com/

**PowerShell Test:**
```powershell
Invoke-RestMethod -Uri "https://ai-lead-scoring.onrender.com/" -Method GET
```

**cURL Test:**
```bash
curl https://ai-lead-scoring.onrender.com/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Lead Qualification API",
  "version": "1.0.0",
  "endpoints": {
    "POST /offer": "Create product/offer",
    "POST /leads/upload": "Upload leads CSV",
    "POST /score": "Score leads",
    "GET /results": "Get scored results",
    "GET /results/export": "Export results as CSV"
  }
}
```

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your OpenAI API key

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

Local API will be available at `http://127.0.0.1:8000/`

## 📚 API Endpoints

### 🌐 Live API Base URL: `https://ai-lead-scoring.onrender.com/`
### 💻 Local Development: `http://127.0.0.1:8000/`

### 1. **GET /** - API Status
Health check and endpoint information.

**Response:**
```json
{
  "status": "healthy",
  "service": "Lead Qualification API",
  "version": "1.0.0",
  "endpoints": {
    "POST /offer": "Create product/offer",
    "POST /leads/upload": "Upload leads CSV",
    "POST /score": "Score leads",
    "GET /results": "Get scored results",
    "GET /results/export": "Export results as CSV"
  }
}
```

### 2. **POST /offer** - Create Product/Offer

**Request Body:**
```json
{
  "name": "AI Outreach Automation",
  "value_props": ["24/7 outreach", "6x more meetings"],
  "ideal_use_cases": ["B2B SaaS mid-market"]
}
```

**Response:**
```json
{
  "id": 1,
  "name": "AI Outreach Automation",
  "value_props": ["24/7 outreach", "6x more meetings"],
  "ideal_use_cases": ["B2B SaaS mid-market"],
  "created_at": "2025-09-15T22:42:24.123Z"
}
```

### 3. **POST /leads/upload** - Upload Leads CSV

**Request:** Multipart form with CSV file

**CSV Format:**
```csv
name,role,company,industry,location,linkedin_bio
Ava Patel,Head of Growth,FlowMetrics,SaaS,San Francisco,VP of Growth at FlowMetrics...
John Smith,CTO,TechCorp,Technology,New York,Chief Technology Officer...
```

**Response:**
```json
{
  "message": "Successfully uploaded 25 leads",
  "batch_id": "batch_a1b2c3d4_1726441344",
  "leads_created": 25
}
```

### 4. **POST /score** - Score Leads

**Request Body:**
```json
{
  "offer_id": 1,
  "batch_id": "batch_a1b2c3d4_1726441344"  // optional
}
```

**Response:**
```json
{
  "message": "Successfully scored 25 leads",
  "total_leads": 25,
  "scored_leads": 25,
  "offer_id": 1,
  "batch_id": "batch_a1b2c3d4_1726441344"
}
```

### 5. **GET /results** - Get Scored Results

**Query Parameters:**
- `offer_id` (optional): Filter by offer
- `batch_id` (optional): Filter by batch
- `intent` (optional): Filter by intent level (High/Medium/Low)

**Response:**
```json
[
  {
    "name": "Ava Patel",
    "role": "Head of Growth",
    "company": "FlowMetrics",
    "intent": "High",
    "score": 85,
    "reasoning": "Fits decision maker role, exact ICP match. Strong profile indicates high potential for AI automation tools."
  }
]
```

### 6. **GET /results/export** - Export Results as CSV

Same query parameters as `/results`. Returns CSV file for download.

## 🧮 Scoring System

### Rule-Based Scoring (Max 50 points)

#### Role Relevance (0-20 points)
- **Decision Makers (20 pts)**: CEO, CTO, VP, Director, Head of, Manager, Founder
- **Influencers (10 pts)**: Senior roles, Specialists, Project Managers
- **Others (0 pts)**: Junior roles, Individual contributors

#### Industry Match (0-20 points)
- **Exact Match (20 pts)**: Industry directly matches ideal use cases
- **Adjacent Match (10 pts)**: Related industries (e.g., SaaS → Software → Technology)
- **No Match (0 pts)**: Unrelated industries

#### Data Completeness (0-10 points)
- **Complete Profile (10 pts)**: All fields filled (name, role, company, industry, location, bio)
- **Mostly Complete (5 pts)**: 4+ fields filled
- **Incomplete (0 pts)**: <4 fields filled

### AI Scoring (Max 50 points)

Uses OpenAI GPT-3.5-turbo to analyze:
- Role-to-product fit
- Industry alignment
- Profile quality and completeness
- Likelihood to benefit from the offer

**Intent Mapping:**
- High Intent: 50 points
- Medium Intent: 30 points  
- Low Intent: 10 points

### Final Classification

- **High (70-100)**: Strong fit, decision-making authority, complete profile
- **Medium (40-69)**: Good fit, some authority or good profile
- **Low (0-39)**: Poor fit, limited authority, incomplete profile

## 🔧 Configuration

### Environment Variables (.env)

```bash
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI API Key (required for AI scoring)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Alternative AI provider
# GEMINI_API_KEY=your_gemini_api_key_here

# File upload limits
MAX_FILE_SIZE=10485760  # 10MB
MAX_LEADS_PER_UPLOAD=1000

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🧪 Testing

### Manual Testing

1. **Test API Status**
```bash
curl http://127.0.0.1:8000/
```

2. **Create an Offer**
```bash
curl -X POST http://127.0.0.1:8000/offer/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 outreach", "6x more meetings"],
    "ideal_use_cases": ["B2B SaaS mid-market"]
  }'
```

3. **Upload Leads CSV**
```bash
curl -X POST http://127.0.0.1:8000/leads/upload/ \
  -F "file=@sample_leads.csv"
```

4. **Score Leads**
```bash
curl -X POST http://127.0.0.1:8000/score/ \
  -H "Content-Type: application/json" \
  -d '{
    "offer_id": 1,
    "batch_id": "your_batch_id"
  }'
```

5. **Get Results**
```bash
curl http://127.0.0.1:8000/results/
```

### Sample CSV File

Create `sample_leads.csv`:
```csv
name,role,company,industry,location,linkedin_bio
Ava Patel,Head of Growth,FlowMetrics,SaaS,San Francisco,VP of Growth at FlowMetrics focused on scaling B2B SaaS companies
John Smith,CTO,TechCorp,Technology,New York,Chief Technology Officer with 10+ years in enterprise software development
Sarah Johnson,Marketing Manager,StartupCo,Software,Austin,Digital marketing specialist helping SaaS companies grow their user base
```

## 🧪 Complete Testing Guide

### 1. Quick Status Check

**Live API Status:**
```bash
# Browser: Visit https://ai-lead-scoring.onrender.com/
# PowerShell:
Invoke-RestMethod -Uri "https://ai-lead-scoring.onrender.com/" -Method GET
# cURL:
curl https://ai-lead-scoring.onrender.com/
```

### 2. Full API Testing

**Automated Testing (Recommended):**
```bash
# Run the comprehensive test suite
python test_api.py
```

**Manual Testing Examples:**

```bash
# 1. Create an offer
curl -X POST https://ai-lead-scoring.onrender.com/offer/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Sales Tool",
    "value_props": ["Automate outreach", "Increase meetings"],
    "ideal_use_cases": ["B2B SaaS companies"]
  }'

# 2. Upload leads (using sample file)
# Visit the API docs or use the test_api.py script

# 3. Score leads
curl -X POST https://ai-lead-scoring.onrender.com/score/ \
  -H "Content-Type: application/json" \
  -d '{"offer_id": 1}'

# 4. Get results
curl https://ai-lead-scoring.onrender.com/results/

# 5. Export CSV
curl https://ai-lead-scoring.onrender.com/results/export/ -o results.csv
```

**PowerShell Testing:**
```powershell
# Run the PowerShell test script
.\test_deployed_api.ps1
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django REST   │    │   Scoring       │    │   OpenAI API    │
│   Framework     │────│   Service       │────│   Integration   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
┌─────────────────┐    ┌─────────────────┐
│   SQLite DB     │    │   File Upload   │
│   (Models)      │    │   Handler       │
└─────────────────┘    └─────────────────┘
```

### Key Components

- **Models**: `Offer`, `Lead`, `LeadScore` - Data structure
- **Serializers**: Request/response validation and formatting
- **Views**: API endpoint implementations
- **Services**: Business logic for scoring algorithms
- **Settings**: Configuration and environment management

## 📋 Requirements

- Python 3.10+
- Django 4.2.7
- Django REST Framework 3.14.0
- OpenAI API Key (for AI scoring)
- Additional dependencies in `requirements.txt`

## 🚨 Error Handling

The API includes comprehensive error handling:

- **Validation Errors**: Invalid input data
- **File Upload Errors**: Incorrect CSV format, file size limits
- **AI Service Errors**: OpenAI API failures with fallback logic
- **Database Errors**: Model validation and constraint violations

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or issues, please create an issue in the repository or contact the development team.

---

**Ready to qualify your leads with AI? Start with the Quick Start guide above!** 🚀