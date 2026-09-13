# Lightweight background watchdog for the pilot run (2026-09-13): logs GPU
# temp/utilization/power draw, overall CPU%, and free RAM every interval to
# a CSV, so that if the machine gets hot/unresponsive again there is a
# timestamped record covering the actual incident instead of a single
# snapshot taken after the fact. Read-only -- takes no action on the
# system, just observes and appends.
#
# Run from an ordinary (non-admin) PowerShell window, left open for the
# duration of a pilot phase:
#   powershell -File scripts\monitor_thermals.ps1
# Stop with Ctrl+C. Log is written to results\thermal_log.csv (relative to
# repo root) and can be opened in Excel or plotted later.

param(
    [int]$IntervalSeconds = 30,
    [string]$OutPath = "$PSScriptRoot\..\results\thermal_log.csv"
)

$header = "timestamp,cpu_percent,free_ram_gb,gpu_temp_c,gpu_util_percent,gpu_power_w"
if (-not (Test-Path $OutPath)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $OutPath) | Out-Null
    Set-Content -Path $OutPath -Value $header -Encoding utf8
}

Write-Host "Logging every $IntervalSeconds s to $OutPath. Ctrl+C to stop."

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
    $mem = Get-CimInstance Win32_OperatingSystem
    $freeRamGb = [math]::Round($mem.FreePhysicalMemory / 1MB, 1)

    $gpuLine = (nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,power.draw --format=csv,noheader,nounits) -split ','
    $gpuTemp = $gpuLine[0].Trim()
    $gpuUtil = $gpuLine[1].Trim()
    $gpuPower = $gpuLine[2].Trim()

    $row = "$timestamp,$([math]::Round($cpu,1)),$freeRamGb,$gpuTemp,$gpuUtil,$gpuPower"
    Add-Content -Path $OutPath -Value $row
    Start-Sleep -Seconds $IntervalSeconds
}
