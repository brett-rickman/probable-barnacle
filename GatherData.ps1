$timestamp = get-date -UFormat "%Y%m%d%H%M"
$dns_reg_file = $env:ComputerName + "_" + $timestamp + "_dns.reg"
$dns_csv_file = $env:ComputerName + "_" + $timestamp + "_dns_zones.csv"
$zone_list_file = $env:ComputerName + "_" + $timestamp + "_zl.txt"
$dhcp_export_file = $env:ComputerName + "_" + $timestamp + "_netsh_dhcp.txt"
$dhcp_export_xml = $env:ComputerName + "_" + $timestamp + "_dhcp.xml"
if (Get-WindowsFeature DNS | where {$_.Installed -eq 1}) {
    echo "DNS Installed."
    reg export "HKLM\Software\Microsoft\Windows NT\CurrentVersion\DNS Server\Zones" $dns_reg_file
    $z = Get-DnsServerZone
    $z | Export-Csv -Path $dns_csv_file -NoTypeInformation
    $z.ZoneName | select-string -pattern '^((0|127|255).in-addr.arpa|TrustAnchors)' -NotMatch | foreach  {
           echo $_ >> $zone_list_file
           $zone_file = "db" + "_" + $timestamp + "_" + $_
           Export-DnsServerZone -FileName $zone_file -Name $_
           Copy-Item -Path $env:Systemroot\system32\dns\$zone_file -Destination .
           Remove-Item -Path $env:SystemRoot\system32\dns\$zone_file 
           }

    } else {
    echo "Skipping DNS collection because DNS role is not installed on $env:ComputerName."
    }
if (Get-WindowsFeature DHCP | where {$_.Installed -eq 1}) {
    echo "DHCP Installed."
    Export-DhcpServer -File $dhcp_export_xml
    netsh dhcp server dump > $dhcp_export_file
    } else {
    echo "Skipping DHCP collection because DHCP role is not installed on $env:ComputerName."
    }
