# ====== CONFIG ======
$token = "eyJraWQiOiJyak1IbVR4eXNmNzRTcFZcL0c4UzBWVFZYQ3pxMEowUVwvRlZ0XC83dVwveFZCUT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJlNDM4MDRmOC0xMGExLTcwNTMtYzg3OS0zMGY4YmJiMzI0ZjkiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfbVF5U21MdGp5IiwiY29nbml0bzp1c2VybmFtZSI6ImU0MzgwNGY4LTEwYTEtNzA1My1jODc5LTMwZjhiYmIzMjRmOSIsIm9yaWdpbl9qdGkiOiJhNzI3ZjYxYS1lNmExLTRkM2QtYTg5Ni1mNmJkMGEzMzEyY2YiLCJhdWQiOiIyMnM5MDJsODFoZWhtM3Y0NnNyaW5qMDZhcSIsImV2ZW50X2lkIjoiZDE3NzBlZWMtMjM5NC00NGFlLWFmMTMtYWRlYTE4NzNhNGI4IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NzUxOTk1NDksImV4cCI6MTc3NTIwMzE0OSwiaWF0IjoxNzc1MTk5NTQ5LCJqdGkiOiI1YjM3NDc4NS00NWMfopKmuS_Q-VE8muNkqsl_BL3MgRIzAiCJVrV7Kde3eCpkLTZ99MbsRISfm3FjKyRX015NqgnijDfWa6aNfzSRYCVgwwfJEw41TFKtU3FT7KddIE9QBmU0wYGm0zBLoxkyUXu3b5-YPX5fpxbe_cepRQU1cmx9R6YixjtdsfzXcMbGWdNvK0YBVlNvdhwlZQHwd9210qPRW2tS-HATOBc62RH7XObMM6ux71ef2vMGmtuwZV4anQ"
$apiUrl = "https://qibe9nyba2.execute-api.us-east-1.amazonaws.com"  # Thay bằng API của bạn

# ====== Kiểm tra token còn hạn ======
$payload = $token.Split('.')[1]

# Chuyển Base64URL -> Base64 chuẩn
$payload = $payload.Replace('-','+').Replace('_','/')
switch ($payload.Length % 4) {
    2 { $payload += "==" }
    3 { $payload += "=" }
}

# Decode
$payloadDecoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($payload))

# Chuyển sang object
$payloadObj = $payloadDecoded | ConvertFrom-Json

# Check exp
$exp = [DateTimeOffset]::FromUnixTimeSeconds($payloadObj.exp).ToLocalTime()
$now = Get-Date
Write-Host "Token expires at: $exp"
Write-Host "Current time: $now"

if ($exp -gt $now) { Write-Host "Token vẫn còn hạn ✅" } else { Write-Host "Token đã hết hạn ❌" }

# ====== Set headers ======
$headers = @{
    "Authorization" = "Bearer $token"
}

# ====== Lấy danh sách incidents ======
try {
    $incidents = Invoke-RestMethod -Uri "$apiUrl/incidents" -Method Get -Headers $headers
    Write-Host "Danh sách incidents:"
    $incidents | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Lỗi khi lấy incidents:" $_.Exception.Message -ForegroundColor Red
    return
}

# ====== Chọn incident để comment ======
$incidentId = Read-Host "Nhập incident_id muốn comment"

# ====== Thêm comment ======
$commentBody = @{
    comment = "Hello Jira comment from API"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$apiUrl/incidents/$incidentId/comments" -Method Post -Headers $headers -Body $commentBody
    Write-Host "Comment đã gửi thành công!"
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Lỗi khi gửi comment:" $_.Exception.Message -ForegroundColor Red
}