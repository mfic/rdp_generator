#Requires -Modules ActiveDirectory

<#
.SYNOPSIS
    Queries Active Directory for Windows Server machines and generates a YAML input file
    for the RDP Generator.
#>

$ErrorActionPreference = "Stop"

# --- Prompt for default username ---
$defaultUsername = Read-Host "Enter the default username (e.g. user@domain.com)"
if (-not $defaultUsername) {
    Write-Error "Username cannot be empty."
    exit 1
}

# --- Prompt for output file name ---
$outputName = Read-Host "Enter a name for the output file (without extension, e.g. customer-name)"
if (-not $outputName) {
    Write-Error "Output name cannot be empty."
    exit 1
}

# --- Query AD ---
Write-Host "`nQuerying Active Directory for Windows Server computers..." -ForegroundColor Cyan

try {
    $servers = Get-ADComputer -Filter { OperatingSystem -like "Windows Server*" } `
        -Properties Name, DNSHostName, OperatingSystem |
        Sort-Object Name
} catch {
    Write-Error "Failed to query Active Directory: $_"
    exit 1
}

if ($servers.Count -eq 0) {
    Write-Warning "No Windows Server computers found in Active Directory."
    exit 0
}

Write-Host "Found $($servers.Count) server(s).`n" -ForegroundColor Green

# --- Build YAML ---
$lines = @("servers:")

foreach ($server in $servers) {
    $address = if ($server.DNSHostName) { $server.DNSHostName } else { $server.Name }
    # Sanitize name: replace spaces and disallowed chars with dashes
    $safeName = $server.Name -replace '[^\w\-\.\@]', '-'

    $lines += "  - name: $safeName"
    $lines += "    address: $address"
    $lines += "    username: $defaultUsername"
}

# --- Write output ---
$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputDir  = Join-Path $scriptDir "input"
$outputFile = Join-Path $outputDir "$outputName.yml"

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$lines | Set-Content -Path $outputFile -Encoding UTF8

Write-Host "YAML file written to: $outputFile" -ForegroundColor Green
Write-Host "Review and edit it as needed, then run main.py to generate the .rdp files."
