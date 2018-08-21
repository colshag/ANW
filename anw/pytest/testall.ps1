# worst script ever

$env:PYTHONPATH = "..\Packages"


function Get-ScriptDirectory
{
    $Invocation = (Get-Variable MyInvocation -Scope 1).Value;
    if($Invocation.PSScriptRoot)
    {
        $Invocation.PSScriptRoot;
    }
    Elseif($Invocation.MyCommand.Path)
    {
        Split-Path $Invocation.MyCommand.Path
    }
    else
    {
        $Invocation.InvocationName.Substring(0,$Invocation.InvocationName.LastIndexOf("\"));
    }
}

Set-Location ..\..\anwgae
write-host $pwd
$dev_appserver = $(get-command dev_appserver.py).Definition

# for some reason this isn't working. need to use the next way for some rason.
#$arguments = $dev_appserver, "--port", "8090", "--admin_port", "8091", "--clear_datastore", "true", "anetwars"
#$dev_server_pid = Start-Process python -ArgumentList $arguments -PassThru 

$arguments = "--port", "8090", "--admin_port", "8091", "--clear_datastore", "true", "anetwars"

$dev_server_pid = Start-Process $dev_appserver -ArgumentList $arguments -PassThru 

$location = get-scriptdirectory
Set-Location $location

# give server time to start
Start-Sleep 5

py.test --showlocals -vv

# can't figure out corret powershell invocation for this. 
taskkill /PID $dev_server_pid.Id /T /F
