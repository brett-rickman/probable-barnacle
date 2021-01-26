param (
    [String]$FilePrefix = "db_202009011510_",
    [String]$BaseDir = "work",
    [string]$InDir = $BaseDir + "/" + "in",
    [String]$ProcDir = $BaseDir + "/proc",
    [String]$OutDir = $BaseDir + "/out",
    [string]$LogDir = $BaseDir + "/log",
    [string]$ZoneCsvFile =  "dns_zones.csv",
    [string]$NamedConf = $BaseDir + "/" + "named.conf"
)

# Template for named.conf entry
$NamedTmpl = @"
zone "__zone_name__" {
    type __zone_type__;
    file "__zone_file__";
};

"@
#Check for needed folders
$DirList = @("in","out","proc","log")
foreach ($dir in $DirList) {
    $TargetDir = join-path -path $BaseDir -childpath $dir 
    if ((test-path -path $TargetDir) -eq $false) {
        new-item -Path $BaseDir -ItemType "directory" -Name $dir 
    }
}
# Process each zone in generated CSV file
$ZoneCsv = $BaseDir + "/" + $ZoneCsvFile
$ZoneList = import-csv $ZoneCsv
foreach ($zone_entry in $ZoneList) {
    $zone_name = $zone_entry."ZoneName"
    # Ignore built-in zones
    if ( $zone_name -eq "0.in-addr.arpa" -or $zone_name -eq "255.in-addr.arpa" -or $zone_name -eq "127.in-addr.arpa" -or $zone_name -eq "TrustAnchors") {
        continue
    }
    # Translate zone type from MS to ISC
    $zone_type = $zone_entry."ZoneType" -replace 'Primary', 'master'
    $zf_file = $BaseDir + "/" + $FilePrefix + $zone_name 
    $proc_file = $ProcDir + "/" + $FilePrefix + $zone_name + ".proc"
    $compiled_file = $OutDir + "/" + $FilePrefix + $zone_name + ".compilezone"
    $ErrorFile = $LogDir + "/" + $zone_name + "_zone_errors.log"
    $WarningFile = $LogDir + "/" + $zone_name + "_zone_warnings.log"
    # Build named.conf entry
    $NamedEntry = $NamedTmpl -replace '__zone_name__', $zone_name
    $NamedEntry = $NamedEntry -replace '__zone_type__', $zone_type
    $NamedEntry = $NamedEntry -replace '__zone_file__', (Get-Item $compiled_file).Basename  
    # Clean up zone file and validate it against BIND
    get-content $zf_file | foreach-object { $_ -replace '\[AGE:\d+\]', ''} | out-file -FilePath $proc_file -encoding ascii 
    start-process -FilePath "named-compilezone" -NoNewWindow -RedirectStandardError $ErrorFile -RedirectStandardOutput $WarningFile `
    -ArgumentList "-k", "ignore", "-o", $compiled_file, $zone_name, $proc_file    
    $NamedEntry | out-file -FilePath $NamedConf -encoding ascii -Append
}