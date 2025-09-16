#!/usr/bin/env python3
"""
Automated API Testing Script for Lead Qualification API
Run this script to test all endpoints automatically.
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000"
CSV_FILE = "sample_leads.csv"

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def print_response(response):
    print(f"Status Code: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Response: {response.text[:200]}...")

def test_api():
    print("🚀 Starting Lead Qualification API Test Suite")
    print(f"Base URL: {BASE_URL}")
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: {CSV_FILE} not found in current directory")
        return False
    
    try:
        # Step 1: Status Check
        print_step(1, "API Status Check - GET /")
        response = requests.get(f"{BASE_URL}/")
        print_response(response)
        
        if response.status_code != 200:
            print("❌ API is not responding correctly")
            return False
        print("✅ API Status Check: PASSED")
        
        # Step 2: Create Offer
        print_step(2, "Create Offer - POST /offer/")
        offer_data = {
            "name": "AI Outreach Automation",
            "value_props": ["24/7 outreach", "6x more meetings", "Automated follow-ups"],
            "ideal_use_cases": ["B2B SaaS", "mid-market", "sales teams"]
        }
        
        response = requests.post(f"{BASE_URL}/offer/", json=offer_data)
        print_response(response)
        
        if response.status_code != 201:
            print("❌ Failed to create offer")
            return False
            
        offer = response.json()
        offer_id = offer["id"]
        print(f"✅ Offer Created: ID = {offer_id}")
        
        # Step 3: Upload Leads
        print_step(3, f"Upload Leads CSV - POST /leads/upload/")
        with open(CSV_FILE, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/leads/upload/", files=files)
        
        print_response(response)
        
        if response.status_code != 201:
            print("❌ Failed to upload leads")
            return False
            
        upload_result = response.json()
        batch_id = upload_result["batch_id"]
        leads_count = upload_result["leads_created"]
        print(f"✅ Leads Uploaded: {leads_count} leads, Batch ID = {batch_id}")
        
        # Step 4: Score Leads
        print_step(4, "Score Leads - POST /score/")
        score_data = {
            "offer_id": offer_id,
            "batch_id": batch_id
        }
        
        response = requests.post(f"{BASE_URL}/score/", json=score_data)
        print_response(response)
        
        if response.status_code != 200:
            print("❌ Failed to score leads")
            return False
            
        scoring_result = response.json()
        scored_count = scoring_result["scored_leads"]
        print(f"✅ Leads Scored: {scored_count} leads processed")
        
        # Step 5: Get Results
        print_step(5, "Get Results - GET /results/")
        response = requests.get(f"{BASE_URL}/results/")
        print_response(response)
        
        if response.status_code != 200:
            print("❌ Failed to get results")
            return False
            
        results = response.json()
        # Handle paginated response
        if isinstance(results, dict) and 'results' in results:
            results_list = results['results']
        else:
            results_list = results
            
        print(f"✅ Results Retrieved: {len(results_list)} scored leads")
        
        # Show sample results
        if results_list:
            print("\n📊 Sample Results:")
            for i, result in enumerate(results_list[:3]):  # Show first 3
                print(f"  {i+1}. {result['name']} ({result['company']}) - {result['intent']} Intent - Score: {result['score']}")
        
        # Step 6: Filter Results by Intent
        print_step(6, "Filter Results - GET /results/?intent=High")
        response = requests.get(f"{BASE_URL}/results/?intent=High")
        print_response(response)
        
        if response.status_code == 200:
            high_intent_results = response.json()
            # Handle paginated response
            if isinstance(high_intent_results, dict) and 'results' in high_intent_results:
                high_intent_list = high_intent_results['results']
            else:
                high_intent_list = high_intent_results
            print(f"✅ High Intent Leads: {len(high_intent_list)} found")
        
        # Step 7: Export CSV
        print_step(7, "Export Results to CSV - GET /results/export/")
        response = requests.get(f"{BASE_URL}/results/export/")
        
        if response.status_code == 200:
            # Save the CSV file
            with open("test_results_export.csv", "wb") as f:
                f.write(response.content)
            print(f"✅ CSV Export: Saved to test_results_export.csv")
            print(f"File size: {len(response.content)} bytes")
        else:
            print("❌ Failed to export CSV")
            return False
        
        # Summary
        print_step("SUMMARY", "Test Results")
        print("✅ All API endpoints tested successfully!")
        print(f"✅ Created offer with ID: {offer_id}")
        print(f"✅ Uploaded {leads_count} leads in batch: {batch_id}")
        print(f"✅ Scored {scored_count} leads")
        print(f"✅ Retrieved {len(results_list)} results")
        print(f"✅ Found {len(high_intent_list)} high-intent leads")
        print("✅ Exported results to CSV")
        
        # Display scoring breakdown
        if results_list:
            high_count = len([r for r in results_list if r['intent'] == 'High'])
            medium_count = len([r for r in results_list if r['intent'] == 'Medium']) 
            low_count = len([r for r in results_list if r['intent'] == 'Low'])
            
            print(f"\n📈 Scoring Breakdown:")
            print(f"   High Intent (70+): {high_count} leads")
            print(f"   Medium Intent (40-69): {medium_count} leads") 
            print(f"   Low Intent (<40): {low_count} leads")
        
        print("\n🎉 ALL TESTS PASSED! The API is working perfectly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the API server")
        print("Make sure the Django server is running:")
        print("   python manage.py runserver")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Lead Qualification API - Automated Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running at {BASE_URL}")
    except:
        print(f"❌ Server is not running at {BASE_URL}")
        print("Please start the Django server first:")
        print("   venv\\Scripts\\activate")
        print("   python manage.py runserver")
        exit(1)
    
    success = test_api()
    
    if success:
        print("\n🚀 Ready for production! All endpoints working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        exit(1)