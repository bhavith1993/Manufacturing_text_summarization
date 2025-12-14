## Demo

Endpoint (POST): `https://ejnn4oexp1.execute-api.us-west-2.amazonaws.com/prod/assist`

### Example request (PowerShell)
```powershell
$uri = "https://ejnn4oexp1.execute-api.us-west-2.amazonaws.com/prod/assist"
$body = @{
  task = "SOP"
  process = "Packaging line"
  issue = "Label misalignment"
  constraints = "Keep it under 10 bullets. Include safety checks and acceptance criteria."
  audience = "operators"
  tone = "clear and practical"
} | ConvertTo-Json

$result = Invoke-RestMethod -Method Post -Uri $uri -ContentType "application/json" -Body $body
$result | ConvertTo-Json -Depth 10
