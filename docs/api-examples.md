# Local API Examples

Start the service on `127.0.0.1:8080`. These examples use only the synthetic lab.

## Health

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health
```

## Fleet

```powershell
$headers = @{ "X-Lab-Token" = "observer-local-token" }
Invoke-RestMethod http://127.0.0.1:8080/api/v1/fleet -Headers $headers
```

## Validate a mission

```powershell
$headers = @{ "X-Lab-Token" = "operator-local-token" }
$body = @{
  mission_id = "MSN-DEMO-001"
  drone_id = "UAS-001"
  mission_type = "training"
  waypoints = @(
    @{ x_m = -40; y_m = 25; altitude_m = 60 },
    @{ x_m = 20; y_m = 70; altitude_m = 80 }
  )
  battery_pct = 82
  estimated_duration_min = 25
  reserve_battery_pct = 20
  link_quality_pct = 91
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  http://127.0.0.1:8080/api/v1/missions/validate `
  -Method Post -Headers $headers -ContentType "application/json" -Body $body
```

## Submit telemetry

```powershell
$headers = @{ "X-Lab-Token" = "operator-local-token" }
$body = @{
  drone_id = "UAS-001"
  sequence = 1
  sent_at = (Get-Date).ToUniversalTime().ToString("o")
  x_m = 20
  y_m = 70
  altitude_m = 80
  battery_pct = 71
  link_quality_pct = 90
  sensor_confidence = 0.95
  mode = "active"
} | ConvertTo-Json

Invoke-RestMethod `
  http://127.0.0.1:8080/api/v1/telemetry `
  -Method Post -Headers $headers -ContentType "application/json" -Body $body
```

## Submit a safe command

```powershell
$headers = @{ "X-Lab-Token" = "operator-local-token" }
$body = @{
  command_id = "CMD-DEMO-001"
  drone_id = "UAS-001"
  action = "hold"
  issued_at = (Get-Date).ToUniversalTime().ToString("o")
  ttl_seconds = 15
  reason = "Local assurance demonstration"
} | ConvertTo-Json

Invoke-RestMethod `
  http://127.0.0.1:8080/api/v1/commands/safe `
  -Method Post -Headers $headers -ContentType "application/json" -Body $body
```

## Read audit events

```powershell
$headers = @{ "X-Lab-Token" = "auditor-local-token" }
Invoke-RestMethod http://127.0.0.1:8080/api/v1/audit/events -Headers $headers
```
