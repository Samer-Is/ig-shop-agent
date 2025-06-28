# COMPREHENSIVE BACKEND TEST FOR REACT APP

$baseUrl = "https://igshop-dev-functions-v2.azurewebsites.net/api"

Write-Host "🧪 TESTING COMPLETE BACKEND FOR REACT APP" -ForegroundColor Cyan
Write-Host "Backend URL: $baseUrl" -ForegroundColor Yellow

# Function to test endpoint
function Test-Endpoint {
    param($endpoint, $method = "GET", $body = $null)
    
    try {
        $url = "$baseUrl$endpoint"
        Write-Host "Testing: $method $endpoint" -ForegroundColor White
        
        $params = @{
            Uri = $url
            Method = $method
            Headers = @{
                "Accept" = "application/json"
                "Content-Type" = "application/json"
            }
        }
        
        if ($body) {
            $params.Body = $body | ConvertTo-Json
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "✅ SUCCESS: $endpoint" -ForegroundColor Green
        
        # Show response data
        if ($response -is [string]) {
            Write-Host "Response: $response" -ForegroundColor Gray
        } else {
            Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
        }
        
        Write-Host ""
        return $true
    }
    catch {
        Write-Host "❌ FAILED: $endpoint" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# Test all endpoints the React app needs
$tests = @(
    @{ endpoint = "/health"; method = "GET" },
    @{ endpoint = "/catalog"; method = "GET" },
    @{ endpoint = "/analytics"; method = "GET" },
    @{ endpoint = "/messages/recent"; method = "GET" },
    @{ endpoint = "/customers"; method = "GET" },
    @{ endpoint = "/ai/test-response"; method = "POST"; body = @{ message = "مرحبا، أريد قميص أبيض" } },
    @{ endpoint = "/ai/test-response"; method = "POST"; body = @{ message = "Hello, I want a white shirt" } },
    @{ endpoint = "/instagram/status"; method = "GET" },
    @{ endpoint = "/instagram/oauth/callback"; method = "POST"; body = @{ code = "test_auth_code_123" } },
    @{ endpoint = "/instagram/status"; method = "GET" },
    @{ endpoint = "/instagram/disconnect"; method = "POST" }
)

$passedTests = 0
$totalTests = $tests.Count

foreach ($test in $tests) {
    if (Test-Endpoint -endpoint $test.endpoint -method $test.method -body $test.body) {
        $passedTests++
    }
}

Write-Host "📊 TEST RESULTS" -ForegroundColor Cyan
Write-Host "Passed: $passedTests/$totalTests" -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } else { "Yellow" })

if ($passedTests -eq $totalTests) {
    Write-Host "🎉 ALL TESTS PASSED! React app should work perfectly!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check the backend deployment." -ForegroundColor Yellow
}

Write-Host "Ready to deploy React app via GitHub Actions!" -ForegroundColor Cyan