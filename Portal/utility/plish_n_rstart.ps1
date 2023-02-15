# Copy files
Copy-Item "\\10.72.176.37\d$\Python Projects\report_portal\Scripts\Portal" "C:\AhmedWebsites\report_portal\Scripts\Portal" -Recurse -Force -Verbose

# Stop services
Stop-Service -Name "Query_Report_Portal"
Stop-Service -Name "UHID Card Generator Website"
Stop-Service -Name "nginx"

# Start services
Start-Service -Name "Query_Report_Portal"
Start-Service -Name "UHID Card Generator Website"
Start-Service -Name "nginx"

# Delete files
Get-ChildItem "C:\AhmedWebsites\report_portal\Scripts\Portal\web_excel_files" | Remove-Item -Force -Verbose

# Append to log file
$date = Get-Date -Format "yyyy-MM-dd"
Add-Content -Path "C:\AhmedWebsites\report_portal\Scripts\restart.log" -Value "$date - Service Restarted Successfully"

# Pause
Read-Host -Prompt "Press Enter to continue"
