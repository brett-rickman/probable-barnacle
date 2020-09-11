param (
    [String]$db_in = "database.bak",
    [String]$db_out = "..\db_fixed.tar.gz",
    [String]$work_dir = ".\db",
    [String]$onedb_in = "onedb.xml",
    [String]$onedb_out = "onedb_fixed.xml"
)
# Extract the backup - assumes 7z.exe is somewhere in $env:path
7z e "$db_in" -w "$work_dir"

# Reset the admin password 
Set-Location -path $work_dir
get-content $onedb_in | foreach-object { 
    if ($_ -match 'VALUE="admin"') { 
        $s = $_ -replace 'PROPERTY NAME="password" VALUE=".+"/>', 'PROPERTY NAME="password" VALUE="infoblox"/>'; $s;
    } else { 
        $_; } } | out-file -filepath $onedb_out -encoding ascii 
remove-item $onedb_in
move-item -path $db_out -Destination $onedb_in 

# Create a new backup file containing the reset password
7z a  -ttar -so -an *.* | 7z a -si $db_out

