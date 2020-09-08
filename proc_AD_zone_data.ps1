param (
    [String]$FilePrefix = "db_202009011510_",
    [String]$InDir = "./in",
    [String]$ProcDir = "./proc",
    [String]$OutDir = "./out",
    [string]$LogDir = "./log"
  
)

#Check for needed folders and create them if necessary
$DirList = @("in","out","proc","log")
foreach ($dir in $DirList) {
    if ((test-path -path $dir) -eq $false) {
        new-item -Path . -ItemType "directory" -Name $dir 
    }
}
# Process each zone file located in $InDir
# Assumes named-compilezone is somewhere in $env:path
foreach ($zf in get-childitem $InDir) {
    $zf_file = $InDir + "/" + $zf."Name"
    $zone_name = $zf."Name" -replace $FilePrefix, ''
    $proc_file = $ProcDir + "/" + $zf."Name" + ".proc"
    $compiled_file = $OutDir + "/" + $zf."Name" + ".compilezone"
    $ErrorFile = $LogDir + "/" + $zone_name + "_errors.log"
    $WarningFile = $LogDir + "/" + $zone_name + "_warnings.log"
    get-content $zf_file | foreach-object { $_ -replace '\[AGE:\d+\]', ''} | out-file -FilePath $proc_file -encoding ascii 
    start-process -FilePath "named-compilezone" -NoNewWindow -RedirectStandardError $ErrorFile -RedirectStandardOutput $WarningFile `
    -ArgumentList "-k", "ignore", "-o", $compiled_file, $zone_name, $proc_file    
}