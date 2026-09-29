$ErrorActionPreference = 'Stop'
# Read-only, targeted searches. Never refresh the full product snapshot here.
$codes = @('10701','777433001200','1032xhs','Sc1003dbc','6928527900105','871392001636','627735189635','10455bbng','420011','209145dxdx827510004140','1043lolo','6976411130176','10291DCQG','9735','1036dgdg','800794207049','4710943100410','4889shj','2008','1017qgqg','6922474188883','0221','HFCXCXC','1012','1006jljl','1018','0030','6941837101611','6922824007468')
$codes += @('1037', '0178')
$rows = foreach ($code in $codes) {
    $url = 'https://stockwise-app-873982544406.us-central1.run.app/api/firebase/products?limit=5&search=' + [uri]::EscapeDataString($code)
    $response = Invoke-RestMethod -Uri $url -TimeoutSec 60
    $matches = @($response.products | Where-Object { $_.code -eq $code -or $_.sku -eq $code })
    # Two active pork-bone records share 0030; keep the verified Tube Bones SKU.
    if ($code -eq '0030') { $matches = @($matches | Where-Object { $_.id -eq 'IkzltGAFYOg74oXtkrXP' }) }
    if ($matches.Count -ne 1) { throw "Expected one exact product for $code; got $($matches.Count)" }
    $p = $matches[0]
    if ($p.isActive -eq $false -or $p.deleted -eq $true) { throw "Inactive product $code" }
    [ordered]@{ code=$code; name=$p.name; id=$p.id; category=$p.category; active=$p.isActive; available_for_delivery=$p.available_for_delivery; stock_quantity=$p.stock_quantity; stock_confidence=$p.stock_confidence; stock_shortfall_kind=$p.stock_shortfall_kind }
    Write-Host "Checked $code $($p.name)"
}
$out = [ordered]@{ checked_at_utc=[DateTime]::UtcNow.ToString('o'); source='StockWise public targeted product search'; scope='Active catalog presence; not a guarantee of physical stock'; products=@($rows) }
$out | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 'docs/content-ingredients-2026-09-29.json'
