param (
    [string]$Exportfile,
    [string]$Rejectsfile = "rejects.txt",
    [string]$WorkDir = "./work"
    )

$obj_types = @()
foreach ($line in get-content -path $Exportfile) {
    $rec = $line | convertfrom-csv -header @(0 .. 0)
    $obj_type = $rec.0
    if ($rec.0 -match '^(H|h)eader-') {
        $obj_type = $obj_type.Substring(7)
        $obj_types += $obj_type
        $last_obj_type = $obj_type 
        }
    if ($obj_types.Contains($obj_type)) {
            $out_file = $WorkDir + "/" + $obj_type + ".csv"
        } else {
            $line
            $out_file = $WorkDir + "/" + $last_obj_type + ".csv"
        }
    $line | out-file -filepath $out_file -encoding utf8 -append 
     
    
    }
    write-output "Found object types ===="
    $obj_types

