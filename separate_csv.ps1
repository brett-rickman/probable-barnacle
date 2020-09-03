param (
    [string]$Exportfile,
    [string]$Rejectsfile = "rejects.txt",
    [string]$WorkDir = "./work"
    )

$CsvIn = import-csv $ExportFile -Header @(0 .. 100) 
$obj_properties = @{}
$sep_csv = @{}
foreach ($row in $CsvIn) {
    $obj_type = $row.0
    if ($obj_type -match '(H|h)eader-') { # found a header row
        $hdrs = $row.psobject.properties.Value | where-object { $_; } 
        $obj_type = $obj_type.Substring(7)
        $obj_properties[$obj_type] = $hdrs
        $sep_csv[$obj_type] = [System.Collections.ArrayList]@()
        } else {
        $h = $obj_properties[$obj_type]
        $r = $row.psobject.properties.Value 
        $this_dat = [ordered]@{}
        for ($i=0; $i -le $h.count - 1; $i++) {
            $k = $h[$i]
            $v = $r[$i] 
            $this_dat[$k] = $v 
            }
        $this_obj = New-Object -TypeName psobject -Property $this_dat
        $sep_csv[$obj_type].Add($this_obj) > $null 
       }
    }
 
foreach ($found_obj_type in $sep_csv.keys) {
    $out_file = $WorkDir + "/sep_" + $found_obj_type + ".csv" 
    $sep_csv[$found_obj_type] | foreach-object { $_; } | export-csv -Path $out_file -Encoding ASCII -NoTypeInformation
    #export-csv -InputObject $sep_csv[$found_obj_type] -Path $out_file -Encoding ASCII -NoTypeInformation
    }
   

   

