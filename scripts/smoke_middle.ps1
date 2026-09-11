# Drives the middle stages of the comment-review chain over a fixture tree,
# for a smoke check that gather through distribute still produces a binder,
# a topology and seeded copies. Provisional -- it drives a prototype surface
# and may be thrown away once that surface settles.

param(
    [string]$Stop,
    [string]$Run
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

# One row per command name, so a rename touches this table alone. Flags for
# each call are written at the call site below.
$Cmd = @{
    gather = 'gather'; topology = 'topology'; distribute = 'distribute'
    mark = 'mark'; check = 'check'; collate = 'collate'
    disposition = 'disposition'; proof = 'proof'; addresser = 'addresser'
}

# The launcher every comment-review command runs through, written once so
# a change to how it is invoked is one edit.
$Launcher = @('uv', 'run', 'python', 'src/comment-review.py')

$RepoRoot = Split-Path -Parent $PSScriptRoot

# Captured before the script ever changes directory, so a relative -Run
# resolves against where the caller stood, not against $RepoRoot below.
$CallerLocation = Get-Location

if (-not $Run) {
    $Run = Join-Path ([System.IO.Path]::GetTempPath()) ("smoke-middle-" + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
} else {
    $Run = [System.IO.Path]::GetFullPath((Join-Path $CallerLocation.Path $Run))
}

# A run never writes inside the repo, so a -Run landing there is refused
# before any work is done.
$RepoRootTrimmed = $RepoRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar)
$RunTrimmed = $Run.TrimEnd([System.IO.Path]::DirectorySeparatorChar)
if ($RunTrimmed -eq $RepoRootTrimmed -or
    $Run.StartsWith($RepoRootTrimmed + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Host "-Run resolves inside the repo: $Run"
    exit 1
}

if (Test-Path -LiteralPath $Run) {
    Write-Host "run directory already exists: $Run"
    exit 1
}

# Quotes each argument that needs it for a faithful paste into PowerShell:
# single-quoted, with an embedded single quote doubled. An argument with
# no space or quote is left bare.
function Format-CommandLine {
    param([Parameter(Mandatory)] [string[]]$CommandLine)
    ($CommandLine | ForEach-Object {
        if ($_ -match '[\s''"]') {
            "'" + ($_ -replace "'", "''") + "'"
        } else {
            $_
        }
    }) -join ' '
}

# Runs one native command, piping its output to the console (Out-Host) so
# a caller capturing this script's own output gets only what it
# Write-Outputs, and checks the exit code against what the stage expects
# (0 unless -Expect says otherwise). On failure -- a wrong exit code or a
# missing executable -- it stops the script, printing the stage name, the
# expected and actual exit codes, the directory it ran from and a command
# line that runs when pasted into PowerShell, so the failure carries its
# own reproduction. $PSNativeCommandUseErrorActionPreference is off
# above, so nothing but this function reports a native failure.
function Invoke-Checked {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [string[]]$CommandLine,
        [int]$Expect = 0
    )
    $exe = $CommandLine[0]
    $rest = @($CommandLine | Select-Object -Skip 1)
    try {
        & $exe @rest | Out-Host
    } catch [System.Management.Automation.CommandNotFoundException] {
        Write-Host "stage failed: $Stage"
        Write-Host "executable not found: $exe"
        Write-Host "directory: $((Get-Location).Path)"
        Write-Host "command: $(Format-CommandLine $CommandLine)"
        exit 1
    }
    if ($LASTEXITCODE -ne $Expect) {
        Write-Host "stage failed: $Stage"
        Write-Host "expected exit code: $Expect"
        Write-Host "actual exit code: $LASTEXITCODE"
        Write-Host "directory: $((Get-Location).Path)"
        Write-Host "command: $(Format-CommandLine $CommandLine)"
        exit $LASTEXITCODE
    }
}

$OriginalDir = Join-Path $Run 'original'
$FixtureFile = Join-Path $OriginalDir 'fib.py'
$BinderFile = Join-Path $Run 'binder.json'
$TopologyFile = Join-Path $Run 'topology.toml'
$CopiesDir = Join-Path $Run 'copies'

# Each entry is one stage's work. Add an entry and its name to $StageOrder
# to extend the chain -- nothing else here needs to change.
$Stages = [ordered]@{
    fixture = {
        New-Item -ItemType Directory -Path $OriginalDir | Out-Null
        Invoke-Checked -Stage 'fixture' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_fixture; write_fixture(Path(sys.argv[1]))',
            $OriginalDir
        )
    }
    gather = {
        Invoke-Checked -Stage 'gather' -CommandLine ($Launcher + @(
            $Cmd.gather, '--repo', $OriginalDir, '--out', $BinderFile, $FixtureFile
        ))
    }
    topology = {
        Invoke-Checked -Stage 'topology-build' -CommandLine ($Launcher + @(
            $Cmd.topology, '--build', '--binder', $BinderFile, '--out', $TopologyFile,
            '--stage', '4=ownership-context,block-context,function-context,module-context'
        ))
        Invoke-Checked -Stage 'topology-verify' -CommandLine ($Launcher + @(
            $Cmd.topology, '--verify', $TopologyFile, '--binder', $BinderFile
        ))
    }
    distribute = {
        Invoke-Checked -Stage 'distribute-4' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--topology', $TopologyFile, '--stage', '4',
            '--binder', $BinderFile, '--out-dir', $CopiesDir
        ))
    }
}

# $PSBoundParameters tells "not given" (run every stage) from "given
# empty" (refused), which $Stop alone cannot: both read as falsy.
if ($PSBoundParameters.ContainsKey('Stop') -and
    ($Stop -eq '' -or $Stages.Keys -notcontains $Stop)) {
    Write-Host "unknown -Stop value: $Stop (valid: $($Stages.Keys -join ', '))"
    exit 1
}

try {
    Set-Location $RepoRoot
    New-Item -ItemType Directory -Path $Run | Out-Null

    foreach ($stageName in $Stages.Keys) {
        & $Stages[$stageName]
        if ($Stop -eq $stageName) {
            break
        }
    }

    Write-Output $Run
}
finally {
    Set-Location $CallerLocation
}
