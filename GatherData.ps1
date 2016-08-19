$timestamp = get-date -UFormat "%Y%m%d%H%M"
$server_info = $env:Computername + "_ver.txt"
$dns_reg_file = $env:ComputerName + "_" + $timestamp + "_dns.reg"
$dns_csv_file = $env:ComputerName + "_" + $timestamp + "_dns_zones.csv"
$zone_list_file = $env:ComputerName + "_" + $timestamp + "_zl.txt"
$dhcp_export_file = $env:ComputerName + "_" + $timestamp + "_netsh_dhcp.txt"
$dhcp_export_xml = $env:ComputerName + "_" + $timestamp + "_dhcp.xml"
$psinfo = Get-Host
$serverver =  (Get-WmiObject -class Win32_OperatingSystem).Caption
echo $serverver > $server_info

if (Get-WindowsFeature DNS | where {$_.Installed -eq 1}) {
    echo "DNS Installed."
    reg export "HKLM\Software\Microsoft\Windows NT\CurrentVersion\DNS Server\Zones" $dns_reg_file
    if ($psinfo.Version -eq "4.0") {
        $z = Get-DnsServerZone
        $z | Export-Csv -Path $dns_csv_file -NoTypeInformation
        $z.ZoneName | select-string -pattern '^((0|127|255).in-addr.arpa|TrustAnchors)' -NotMatch | foreach  {
            echo $_ >> $zone_list_file
            $zone_file = "db" + "_" + $timestamp + "_" + $_
            Export-DnsServerZone -FileName $zone_file -Name $_
            Move-Item -Path $env:Systemroot\system32\dns\$zone_file -Destination . -Force
            }
        } else {
            dnscmd /EnumZones > $zone_list_file
            $zlist = get-content -path $zone_list_file | select-string -pattern "Primary" | 
            select-string -pattern '^((0|127|255).in-addr.arpa|TrustAnchors)' -NotMatch
            $zlist.Line | foreach { 
                $zname = $_ -split (" +") | select -index 1 
                $zone_file =  "db" + "_" + $timestamp + "_" + + $zname
                dnscmd /ZoneExport $zname $zone_file
                move-item -path $env:Systemroot\system32\dns\$zone_file -Destination . -Force
                }
        }

    } else {
    echo "Skipping DNS collection because DNS role is not installed on $env:ComputerName."
    }
if (Get-WindowsFeature DHCP | where {$_.Installed -eq 1}) {
    echo "DHCP Installed."
    if ($psinfo.Version -eq "4.0") {
        Export-DhcpServer -File $dhcp_export_xml
        }
    netsh dhcp server dump > $dhcp_export_file
    } else {
    echo "Skipping DHCP collection because DHCP role is not installed on $env:ComputerName."
}
