
$dns_reg_file = $env:ComputerName + "_dns.reg"
$dns_csv_file = $env:ComputerName + "_dns_zones.csv"
if (Get-WindowsFeature DNS | where {$_.Installed -eq 1}) {
    echo "DNS Installed."
    reg export "HKLM\Software\Microsoft\Windows NT\CurrentVersion\DNS Server\Zones" $dns_reg_file
    Get-DnsServerZone | Export-Csv -Path $dns_csv_file -NoTypeInformation
    } else {
    echo "Skipping DNS collection because DNS role is not installed on $env:ComputerName."
    }
if (Get-WindowsFeature DHCP | where {$_.Installed -eq 1}) {
    echo "DHCP Installed."
    } else {
    echo "Skipping DHCP collection because DHCP role is not installed on $env:ComputerName."
    }
