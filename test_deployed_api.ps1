# Quick test script for the deployed API
$baseUrl = "https://ai-lead-scoring.onrender.com"

Write-Host "Testing API..." -ForegroundColor Green

# Basic status check
Write-Host "\n1. Status check..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    Write-Host "OK - Status: $($status.status)" -ForegroundColor Green
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Try creating an offer
Write-Host "\n2. Create offer test..." -ForegroundColor Yellow
$offerData = @{
    name = "Test Product"
    description = "Testing the API"
    target_industry = "Technology"
    price_range = "10000-50000"
} | ConvertTo-Json

try {
    $offer = Invoke-RestMethod -Uri "$baseUrl/offer/" -Method POST -Body $offerData -ContentType "application/json"
    Write-Host "OK - Created offer ID: $($offer.id)" -ForegroundColor Green
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check upload endpoint
Write-Host "\n3. Upload endpoint check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/leads/upload/" -Method GET
} catch {
    if ($_.Exception.Response.StatusCode -eq 405) {
        Write-Host "OK - Upload endpoint is working" -ForegroundColor Green
    } else {
        Write-Host "Issue: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Check results
Write-Host "\n4. Results endpoint..." -ForegroundColor Yellow
try {
    $results = Invoke-RestMethod -Uri "$baseUrl/results/" -Method GET
    Write-Host "OK - Results accessible" -ForegroundColor Green
} catch {
    Write-Host "Issue: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "\nDone testing!" -ForegroundColor Green