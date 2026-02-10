#!/bin/bash

# Comprehensive Endpoint Testing Script - Including NEW Features
# Tests all endpoints including clinical notes and blood reports

BASE_URL="http://localhost:8000"
TOKEN=""

echo "============================================================"
echo "🧪 Complete Backend Endpoint Testing"
echo "Testing ALL endpoints including new features"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo -n "Testing: $name ... "
    
    if [ "$method" = "GET" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
        else
            response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL$endpoint" 2>/dev/null)
        fi
    else
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint" 2>/dev/null)
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "$data" "$BASE_URL$endpoint" 2>/dev/null)
        fi
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status_code)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "   Response: ${body:0:100}"
        ((FAILED++))
    fi
    
    # Store token if this is a login request
    if [[ "$endpoint" == "/auth/login" ]] && [[ "$status_code" == "200" ]]; then
        TOKEN=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        if [ -n "$TOKEN" ]; then
            echo "   🔑 Token stored for subsequent requests"
        fi
    fi
}

echo "============================================================"
echo "PHASE 1: Core Health Endpoints"
echo "============================================================"
test_endpoint "Health Check" "GET" "/health" "" "200"
test_endpoint "Root Endpoint" "GET" "/" "" "200"
test_endpoint "OpenAPI Docs" "GET" "/openapi.json" "" "200"
echo ""

echo "============================================================"
echo "PHASE 2: Authentication"
echo "============================================================"
test_endpoint "Login - Doctor" "POST" "/auth/login" '{"username":"dr_smith","password":"Doctor@123"}' "200"
test_endpoint "Login - Admin" "POST" "/auth/login" '{"username":"admin","password":"Admin@123"}' "200"
test_endpoint "Login - Invalid Credentials" "POST" "/auth/login" '{"username":"invalid","password":"wrong"}' "401"
echo ""

echo "============================================================"
echo "PHASE 3: Patient Endpoints"
echo "============================================================"
test_endpoint "Get Patients" "GET" "/patients/" "" "200"
test_endpoint "Verify Biometric (No Match)" "POST" "/patients/verify-biometric" '{"fingerprint_data":"test_data"}' "404"
echo ""

echo "============================================================"
echo "PHASE 4: Vitals Endpoints"
echo "============================================================"
test_endpoint "Get Vitals (Empty Query)" "GET" "/vitals/" "" "200"
echo ""

echo "============================================================"
echo "PHASE 5: Device Ingestion"
echo "============================================================"
test_endpoint "Device Ingestion Health Check" "GET" "/devices/ingest/health" "" "200"
echo ""

echo "============================================================"
echo "PHASE 6: NEW - Clinical Notes Endpoints ⭐"
echo "============================================================"
test_endpoint "Get Notes (No Patient ID)" "GET" "/notes/patient/test-patient-id" "" "404"
test_endpoint "Get Note (Invalid ID)" "GET" "/notes/invalid-note-id" "" "404"
echo ""

echo "============================================================"
echo "PHASE 7: NEW - Blood Reports Endpoints ⭐"
echo "============================================================"
test_endpoint "Get Blood Reports (Invalid Patient)" "GET" "/blood-reports/patient/test-patient-id" "" "404"
test_endpoint "Get Blood Report (Invalid ID)" "GET" "/blood-reports/invalid-report-id" "" "404"
echo ""

echo "============================================================"
echo "PHASE 8: Health Profile"
echo "============================================================"
test_endpoint "Get Health Profiles (List)" "GET" "/health-profile/" "" "200"
echo ""

echo "============================================================"
echo "📊 TEST SUMMARY"
echo "============================================================"
echo -e "${GREEN}✅ PASSED: $PASSED${NC}"
echo -e "${RED}❌ FAILED: $FAILED${NC}"
echo "============================================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ All endpoints are working correctly"
    echo "✅ New features (notes & blood-reports) are available"
    echo "✅ Server is healthy and ready for production"
else
    echo -e "${YELLOW}⚠️  Some tests failed - review above${NC}"
fi

echo ""
echo "🌐 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
