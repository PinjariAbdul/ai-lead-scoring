# PowerShell script to test the deployed API
$baseUrl = "https://ai-lead-scoring.onrender.com"

Write-Host "Testing Lead Qualification API..." -ForegroundColor Green

# Test 1: Status Check
Write-Host "`n1. Testing Status..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    Write-Host "✅ Status: $($status.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Status check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Create Offer
Write-Host "`n2. Testing Create Offer..." -ForegroundColor Yellow
$offerData = @{
    name = "Test Product"
    description = "A test product for API testing"
    target_industry = "Technology"
    price_range = "10000-50000"
} | ConvertTo-Json

try {
    $offer = Invoke-RestMethod -Uri "$baseUrl/offer/" -Method POST -Body $offerData -ContentType "application/json"
    Write-Host "✅ Offer created with ID: $($offer.id)" -ForegroundColor Green
    $global:offerId = $offer.id
} catch {
    Write-Host "❌ Create offer failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check if CSV upload endpoint is accessible
Write-Host "`n3. Testing CSV Upload Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/leads/upload/" -Method GET
    if ($response.StatusCode -eq 405) {
        Write-Host "✅ Upload endpoint accessible (Method Not Allowed is expected for GET)" -ForegroundColor Green
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 405) {
        Write-Host "✅ Upload endpoint accessible (Method Not Allowed is expected for GET)" -ForegroundColor Green
    } else {
        Write-Host "❌ Upload endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 4: Check Results endpoint
Write-Host "`n4. Testing Results Endpoint..." -ForegroundColor Yellow
try {
    $results = Invoke-RestMethod -Uri "$baseUrl/results/" -Method GET
    Write-Host "✅ Results endpoint accessible. Found $($results.count) total results" -ForegroundColor Green
} catch {
    Write-Host "❌ Results endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nAPI Testing Complete!" -ForegroundColor Green