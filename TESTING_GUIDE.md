# API Testing Guide

## Complete Step-by-Step Testing

### Prerequisites
- Server running at `http://127.0.0.1:8000/`
- `curl` command available (or use Postman/Insomnia)
- Sample CSV file ready

### 1. ✅ Status Check: GET /

**Test the API health and get endpoint information:**

```bash
curl http://127.0.0.1:8000/
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

### 2. ✅ Create Offer: POST /offer/

**Create a product/offer for lead scoring:**

```bash
curl -X POST http://127.0.0.1:8000/offer/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 outreach", "6x more meetings", "Automated follow-ups"],
    "ideal_use_cases": ["B2B SaaS", "mid-market", "sales teams"]
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "AI Outreach Automation",
  "value_props": ["24/7 outreach", "6x more meetings", "Automated follow-ups"],
  "ideal_use_cases": ["B2B SaaS", "mid-market", "sales teams"],
  "created_at": "2025-09-15T22:42:24.123Z"
}
```

**Save the `id` (e.g., 1) for later steps!**

### 3. ✅ Upload Leads: POST /leads/upload/

**Upload the sample CSV file:**

```bash
curl -X POST http://127.0.0.1:8000/leads/upload/ \
  -F "file=@sample_leads.csv"
```

**Expected Response:**
```json
{
  "message": "Successfully uploaded 10 leads",
  "batch_id": "batch_a1b2c3d4_1726441344",
  "leads_created": 10
}
```

**Save the `batch_id` for later steps!**

### 4. ✅ Score Leads: POST /score/

**Score the uploaded leads against the offer:**

```bash
curl -X POST http://127.0.0.1:8000/score/ \
  -H "Content-Type: application/json" \
  -d '{
    "offer_id": 1,
    "batch_id": "batch_a1b2c3d4_1726441344"
  }'
```

**Note:** Replace `batch_a1b2c3d4_1726441344` with your actual batch_id from step 3.

**Expected Response:**
```json
{
  "message": "Successfully scored 10 leads",
  "total_leads": 10,
  "scored_leads": 10,
  "offer_id": 1,
  "batch_id": "batch_a1b2c3d4_1726441344"
}
```

### 5. ✅ Get Results: GET /results/

**Retrieve all scored results:**

```bash
curl http://127.0.0.1:8000/results/
```

**Expected Response:**
```json
[
  {
    "name": "David Brown",
    "role": "CEO",
    "company": "GrowthHacker",
    "intent": "High",
    "score": 85,
    "reasoning": "Fits decision maker role, exact ICP match. Strong profile indicates high potential for automation tools."
  },
  {
    "name": "Michael Chen",
    "role": "VP Sales",
    "company": "DataFlow",
    "intent": "High",
    "score": 80,
    "reasoning": "Fits decision maker role, adjacent industry. Sales leadership role perfect for outreach automation."
  }
]
```

**Filter by intent level:**
```bash
curl "http://127.0.0.1:8000/results/?intent=High"
```

**Filter by batch:**
```bash
curl "http://127.0.0.1:8000/results/?batch_id=batch_a1b2c3d4_1726441344"
```

### 6. ✅ Export CSV: GET /results/export/

**Download results as CSV file:**

```bash
curl "http://127.0.0.1:8000/results/export/" -o results.csv
```

**Or with filters:**
```bash
curl "http://127.0.0.1:8000/results/export/?intent=High" -o high_intent_leads.csv
```

**Expected CSV content:**
```csv
Name,Role,Company,Industry,Location,Intent,Score,Rule Score,AI Score,Reasoning
David Brown,CEO,GrowthHacker,Enterprise,Chicago,High,85,30,50,"Fits decision maker role, exact ICP match. Strong profile indicates high potential for automation tools."
Michael Chen,VP Sales,DataFlow,B2B,Seattle,High,80,30,50,"Fits decision maker role, adjacent industry. Sales leadership role perfect for outreach automation."
```

## Alternative Testing Methods

### Using PowerShell (Windows)

**1. Status Check:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method GET
```

**2. Create Offer:**
```powershell
$body = @{
    name = "AI Outreach Automation"
    value_props = @("24/7 outreach", "6x more meetings")
    ideal_use_cases = @("B2B SaaS", "mid-market")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/offer/" -Method POST -Body $body -ContentType "application/json"
```

**3. Upload CSV:**
```powershell
$form = @{
    file = Get-Item -Path "sample_leads.csv"
}
Invoke-RestMethod -Uri "http://127.0.0.1:8000/leads/upload/" -Method POST -Form $form
```

### Using Python requests

**Create a test script `test_api.py`:**

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. Status check
response = requests.get(f"{BASE_URL}/")
print("Status:", response.json())

# 2. Create offer
offer_data = {
    "name": "AI Outreach Automation",
    "value_props": ["24/7 outreach", "6x more meetings"],
    "ideal_use_cases": ["B2B SaaS", "mid-market"]
}
response = requests.post(f"{BASE_URL}/offer/", json=offer_data)
offer = response.json()
print("Offer created:", offer)
offer_id = offer["id"]

# 3. Upload leads
with open("sample_leads.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/leads/upload/", files=files)
upload_result = response.json()
print("Upload result:", upload_result)
batch_id = upload_result["batch_id"]

# 4. Score leads
score_data = {
    "offer_id": offer_id,
    "batch_id": batch_id
}
response = requests.post(f"{BASE_URL}/score/", json=score_data)
print("Scoring result:", response.json())

# 5. Get results
response = requests.get(f"{BASE_URL}/results/")
results = response.json()
print("Results:", json.dumps(results, indent=2))

# 6. Export CSV
response = requests.get(f"{BASE_URL}/results/export/")
with open("exported_results.csv", "wb") as f:
    f.write(response.content)
print("CSV exported to exported_results.csv")
```

**Run the test:**
```bash
python test_api.py
```

## Troubleshooting

### Common Issues:

**1. Server not running:**
```bash
# Start the server first
venv\Scripts\activate
python manage.py runserver
```

**2. File not found:**
```bash
# Make sure you're in the correct directory
cd "c:\Users\abdul\OneDrive\Desktop\Kuvaka Tech"
```

**3. OpenAI API key not set:**
- Edit `.env` file and add your OpenAI API key
- Without it, AI scoring will use fallback logic

**4. CSRF errors:**
- The API is configured to handle CSRF properly
- Make sure you're sending proper JSON content-type headers

### Expected Scoring Results:

Based on the sample CSV data:
- **High Intent (70+)**: CEOs, VPs, CTOs in SaaS/Tech companies
- **Medium Intent (40-69)**: Managers, Directors in related industries  
- **Low Intent (<40)**: Junior roles or unrelated industries

## Complete Test Flow Summary

```bash
# 1. Check API status
curl http://127.0.0.1:8000/

# 2. Create offer (save the ID)
curl -X POST http://127.0.0.1:8000/offer/ -H "Content-Type: application/json" -d '{"name":"AI Outreach","value_props":["automation"],"ideal_use_cases":["SaaS"]}'

# 3. Upload leads (save the batch_id)
curl -X POST http://127.0.0.1:8000/leads/upload/ -F "file=@sample_leads.csv"

# 4. Score leads (use offer_id=1 and your batch_id)
curl -X POST http://127.0.0.1:8000/score/ -H "Content-Type: application/json" -d '{"offer_id":1,"batch_id":"your_batch_id"}'

# 5. Get results
curl http://127.0.0.1:8000/results/

# 6. Export CSV
curl "http://127.0.0.1:8000/results/export/" -o results.csv
```

That's it! All endpoints tested successfully! 🎉