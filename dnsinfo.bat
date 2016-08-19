@echo off
rem
rem Get information about DNS zones on this server
rem
del c:\windows\system32\dns\db.*
dnscmd /enumzones > %COMPUTERNAME%_zonelist.txt
for /F %%Z in ('dnscmd /enumzones /primary /secondary') DO dnscmd /ZoneExport %%Z db.%%Z
copy c:\windows\system32\dns\db.*
copy %systemroot%\system32\dns\DnsSettings.txt .
netsh dhcp server dump > %COMPUTERNAME%_netsh.txt
