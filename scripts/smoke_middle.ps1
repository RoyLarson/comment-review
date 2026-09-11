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

$StageOrder = @('fixture', 'gather', 'topology', 'distribute')

if ($Stop -and ($StageOrder -notcontains $Stop)) {
    Write-Host "unknown -Stop value: $Stop (valid: $($StageOrder -join ', '))"
    exit 1
}

$RepoRoot = Split-Path -Parent $PSScriptRoot

if (-not $Run) {
    $Run = Join-Path ([System.IO.Path]::GetTempPath()) ("smoke-middle-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
} else {
    $Run = [System.IO.Path]::GetFullPath($Run)
}

if (Test-Path -LiteralPath $Run) {
    Write-Host "run directory already exists: $Run"
    exit 1
}

# Runs one native command, checks its exit code against what the stage
# expects (0 unless -Expect says otherwise) and stops the script on
# failure -- printing the stage name, the expected and actual exit codes
# and the full command line, so the failure carries its own reproduction.
# A missing executable is caught the same way, naming the stage and
# command instead of an exit code. $PSNativeCommandUseErrorActionPreference
# is off above, so nothing but this function reports a native failure.
function Invoke-Checked {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [string[]]$CommandLine,
        [int]$Expect = 0
    )
    $exe = $CommandLine[0]
    $rest = @($CommandLine | Select-Object -Skip 1)
    try {
        & $exe @rest
    } catch [System.Management.Automation.CommandNotFoundException] {
        Write-Host "stage failed: $Stage"
        Write-Host "executable not found: $exe"
        Write-Host "command: $($CommandLine -join ' ')"
        exit 1
    }
    if ($LASTEXITCODE -ne $Expect) {
        Write-Host "stage failed: $Stage"
        Write-Host "expected exit code: $Expect"
        Write-Host "actual exit code: $LASTEXITCODE"
        Write-Host "command: $($CommandLine -join ' ')"
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
$Stages = @{
    fixture = {
        New-Item -ItemType Directory -Path $OriginalDir | Out-Null
        Invoke-Checked -Stage 'fixture' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_fixture; write_fixture(Path(sys.argv[1]))',
            $OriginalDir
        )
    }
    gather = {
        Invoke-Checked -Stage 'gather' -CommandLine @(
            'uv', 'run', 'python', 'src/comment-review.py', $Cmd.gather,
            '--repo', $OriginalDir, '--out', $BinderFile, $FixtureFile
        )
    }
    topology = {
        Invoke-Checked -Stage 'topology-build' -CommandLine @(
            'uv', 'run', 'python', 'src/comment-review.py', $Cmd.topology,
            '--build', '--binder', $BinderFile, '--out', $TopologyFile,
            '--stage', '4=ownership-context,block-context,function-context,module-context'
        )
        Invoke-Checked -Stage 'topology-verify' -CommandLine @(
            'uv', 'run', 'python', 'src/comment-review.py', $Cmd.topology,
            '--verify', $TopologyFile, '--binder', $BinderFile
        )
    }
    distribute = {
        Invoke-Checked -Stage 'distribute-4' -CommandLine @(
            'uv', 'run', 'python', 'src/comment-review.py', $Cmd.distribute,
            '--topology', $TopologyFile, '--stage', '4',
            '--binder', $BinderFile, '--out-dir', $CopiesDir
        )
    }
}

$CallerLocation = Get-Location
try {
    Set-Location $RepoRoot
    New-Item -ItemType Directory -Path $Run | Out-Null

    foreach ($stageName in $StageOrder) {
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
