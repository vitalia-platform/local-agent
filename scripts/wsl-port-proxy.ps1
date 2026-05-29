# Define ports to forward
$ports = @(5432, 6379, 11434, 4000, 8001)
$listenAddress = "0.0.0.0"

# Get current WSL2 IP address
$wslIp = (wsl.exe hostname -I).Trim()

if (-not $wslIp) {
    Write-Error "Could not determine WSL2 IP address."
    exit
}

# Apply rules
foreach ($port in $ports) {
    # Remove existing rule to avoid conflicts
    netsh interface portproxy delete v4tov4 listenport=$port listenaddress=$listenAddress 2>$null
    
    # Add updated rule
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=$listenAddress connectport=$port connectaddress=$wslIp
    
    # Ensure Firewall allows the port
    New-NetFirewallRule -DisplayName "WSL2 Port $port" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $port -ErrorAction SilentlyContinue
}
