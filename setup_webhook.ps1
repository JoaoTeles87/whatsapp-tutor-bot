# Script to configure Evolution API webhook

$headers = @{
    "apikey" = "429683C4C977415CAAFCCE10F7D57E11"
    "Content-Type" = "application/json"
}

$body = @{
    "url" = "http://localhost:5000/webhook"
    "webhook_by_events" = $false
    "webhook_base64" = $false
    "events" = @(
        "MESSAGES_UPSERT"
    )
} | ConvertTo-Json

$instance = "Pro Letras"
$encodedInstance = [System.Web.HttpUtility]::UrlEncode($instance)

Write-Host "Configuring webhook for instance: $instance"
Write-Host "Webhook URL: http://localhost:5000/webhook"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/webhook/set/$encodedInstance" -Method POST -Headers $headers -Body $body
    Write-Host "✅ Webhook configured successfully!" -ForegroundColor Green
    Write-Host $response | ConvertTo-Json
} catch {
    Write-Host "❌ Error configuring webhook:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
