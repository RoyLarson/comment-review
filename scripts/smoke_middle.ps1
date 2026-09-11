# Drives the middle stages of the comment-review chain over a fixture tree,
# for a smoke check that the chain from gather through disposition still
# composes: a binder, a topology, seeded copies, a planted scenario matrix
# of marks, the fold's proof and the chief's dispositions closing it.
# Provisional -- it drives a prototype surface and may be thrown away once
# that surface settles.

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
    $RandomPart = [System.Guid]::NewGuid().ToString('N').Substring(0, 8)
    $Run = Join-Path ([System.IO.Path]::GetTempPath()) ("smoke-middle-" + (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + $RandomPart)
} else {
    $Run = [System.IO.Path]::GetFullPath($Run, $CallerLocation.ProviderPath)
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

# Formats a command line for a faithful paste into PowerShell: any
# argument -- the executable included -- holding anything besides a
# letter, digit or one of _ . / \ : = , - is single-quoted, with an
# embedded single quote doubled; everything else is left bare. The line
# is prefixed with "& " so a quoted executable (a path with a space)
# still runs -- a bare quoted path is a parse error without the call
# operator.
function Format-CommandLine {
    param([Parameter(Mandatory)] [string[]]$CommandLine)
    $formatted = $CommandLine | ForEach-Object {
        if ($_ -match '^[A-Za-z0-9_./\\:=,-]*$') {
            $_
        } else {
            "'" + ($_ -replace "'", "''") + "'"
        }
    }
    '& ' + ($formatted -join ' ')
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
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
        exit 1
    }
}

$OriginalDir = Join-Path $Run 'original'
$FixtureFile = Join-Path $OriginalDir 'fib.py'
$BinderFile = Join-Path $Run 'binder.json'
$TopologyFile = Join-Path $Run 'topology.toml'
$CopiesDir = Join-Path $Run 'copies'

# The four roles stage 4 dispatches to, and where distribute's own naming
# (`<stage>_<role>_<n>.json`) puts each one's seeded copy. This fixture is
# small enough that stage 4 never shards a role over more than one dispatch,
# so `n` is always 1.
$Roles = @('ownership-context', 'block-context', 'function-context', 'module-context')
$CopyFile = @{}
foreach ($role in $Roles) {
    $CopyFile[$role] = Join-Path $CopiesDir "4_${role}_1.json"
}

$ChiefFile = Join-Path $Run 'chief.json'
$Proof0File = Join-Path $Run 'proof0.json'
$DispositionsFile = Join-Path $Run 'dispositions.json'
$ChiefFinalFile = Join-Path $Run 'chief-final.json'
$FinalFile = Join-Path $Run 'final.json'

# Each entry is one stage's work, and the chain as this script leaves it ends
# at disposition. Add an entry to $Stages to extend it further -- nothing
# else here needs to change.
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
    # The scenario matrix, `docs/superpowers/specs/2026-09-08-the-middle-chain-
    # smoke-design.md`'s "The scenario matrix", planted one `mark` invocation
    # per ruling per role -- no bulk pass, since `mark` itself refuses one.
    # Every one of the nine filled places gets a ruling from every role, so a
    # place the matrix does not otherwise name is marked clean by all four.
    mark = {
        # a0 -- named by nothing else, clean from every role.
        foreach ($role in $Roles) {
            Invoke-Checked -Stage "mark a0 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@a0',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # c12 -- named by nothing else, clean from every role.
        foreach ($role in $Roles) {
            Invoke-Checked -Stage "mark c12 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@c12',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # a1 -- the human query nothing settles. block-context raises it; the
        # other three have nothing to add.
        Invoke-Checked -Stage 'mark a1 block-context query' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@a1',
            '--instruction', 'query', '--shape', 'human-review-necessary',
            '--attempted', 'read the docstring against what logged and wrapper do',
            '--settles', 'human',
            '--reason', 'the docstring and the decorator disagree about what counts',
            '--cite', 'fib.py:10', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark a1 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@a1',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # c6 -- the lone mark. block-context settles it alone; the other three
        # defer with a scope-declaring query rather than clean, per Process #89.
        Invoke-Checked -Stage 'mark c6 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@c6',
            '--instruction', 'correct',
            '--false', "the decorator's whole job", '--true', "the decorator's only job",
            '--reason', 'counting is the whole job of the decorator, worded oddly',
            '--cite', 'fib.py:15', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark c6 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@c6',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'block-context',
                '--reason', "this paragraph's subject is the decorator's own accounting, not my remit",
                '--cite', 'fib.py:15', '--repo', $OriginalDir
            ))
        }
        # c1 -- two differ. block-context and function-context correct the same
        # clause to different text; ownership-context and module-context clean.
        Invoke-Checked -Stage 'mark c1 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@c1',
            '--instruction', 'correct',
            '--false', 'memoised or not', '--true', 'cached or not',
            '--reason', 'the fixture calls this a cache everywhere else',
            '--cite', 'fib.py:6', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark c1 function-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@c1',
            '--instruction', 'correct',
            '--false', 'memoised or not', '--true', 'computed or not',
            '--reason', 'the counter increments whether or not the value was computed',
            '--cite', 'fib.py:6', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'module-context')) {
            Invoke-Checked -Stage "mark c1 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@c1',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # a3 -- three differ. block-, function- and module-context each correct
        # the same clause a third way; ownership-context clean.
        Invoke-Checked -Stage 'mark a3 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@a3',
            '--instruction', 'correct',
            '--false', 'counting from fib(0) = 0', '--true', 'counting up from fib(0) = 0',
            '--reason', "counting up matches the recursion's own direction",
            '--cite', 'fib.py:26', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark a3 function-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@a3',
            '--instruction', 'correct',
            '--false', 'counting from fib(0) = 0', '--true', 'starting at fib(0) = 0',
            '--reason', 'the signature takes n, not a running count',
            '--cite', 'fib.py:26', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark a3 module-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'fib.py@a3',
            '--instruction', 'correct',
            '--false', 'counting from fib(0) = 0', '--true', 'beginning at fib(0) = 0',
            '--reason', "matches the module docstring's own wording",
            '--cite', 'fib.py:26', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark a3 ownership-context clean' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'fib.py@a3',
            '--instruction', 'clean', '--repo', $OriginalDir
        ))
        # b9 -- the recast. block-context and module-context each correct the
        # same clause a different way; ownership-context and function-context
        # clean.
        Invoke-Checked -Stage 'mark b9 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@b9',
            '--instruction', 'correct',
            '--false', 'logged sees', '--true', 'logged watches',
            '--reason', "watches matches the decorator's own verb elsewhere",
            '--cite', 'fib.py:21', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark b9 module-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'fib.py@b9',
            '--instruction', 'correct',
            '--false', 'logged sees', '--true', 'logged tracks',
            '--reason', "tracks matches the module's own CALLS counter",
            '--cite', 'fib.py:21', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context')) {
            Invoke-Checked -Stage "mark b9 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@b9',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # b14 -- the drop. ownership-context drops the paragraph; the other
        # three defer with a scope-declaring query rather than clean.
        Invoke-Checked -Stage 'mark b14 ownership-context drop' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'fib.py@b14',
            '--instruction', 'drop',
            '--drop', '    # Two calls per level, which is what the counter measures.',
            '--reason', 'the line above already names the two recursive calls',
            '--cite', 'fib.py:29', '--repo', $OriginalDir
        ))
        foreach ($role in @('block-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark b14 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@b14',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'ownership-context',
                '--reason', "this paragraph's subject is placement within the body, not my remit",
                '--cite', 'fib.py:29', '--repo', $OriginalDir
            ))
        }
        # b1 -- the move, to b0. ownership-context moves it; the other three
        # defer with a scope-declaring query rather than clean.
        Invoke-Checked -Stage 'mark b1 ownership-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'fib.py@b1',
            '--instruction', 'move', '--from', 'fib.py@b1', '--to', 'fib.py@b0',
            '--change', '# Module state, written by the wrapper and read by the caller.',
            '--reason', 'module state belongs above the import, not below it',
            '--cite', 'fib.py:5', '--repo', $OriginalDir
        ))
        foreach ($role in @('block-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark b1 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@b1',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'ownership-context',
                '--reason', "this paragraph's subject is where module state is declared, not my remit",
                '--cite', 'fib.py:5', '--repo', $OriginalDir
            ))
        }
        # a2 -- the add. function-context is the only role that touches this
        # empty place; wrapper carries no slot in anyone else's copy to rule on.
        Invoke-Checked -Stage 'mark a2 function-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@a2',
            '--instruction', 'add',
            '--missing', 'wrapper has no docstring', '--anchor', '`wrapper`',
            '--anchor-line', '    def wrapper(n):',
            '--change', '"""Count each call, then pass it through."""',
            '--reason', 'wrapper is the declared function; logged only wraps it',
            '--cite', 'fib.py:13', '--repo', $OriginalDir
        ))
    }
    # `check --edit-copy ... --binder ...` over each of the four copies, the
    # same boundary `collate` would apply -- a run that passes here is a copy
    # the fold reads whole.
    check = {
        foreach ($role in $Roles) {
            Invoke-Checked -Stage "check $role" -CommandLine ($Launcher + @(
                $Cmd.check, '--edit-copy', $CopyFile[$role], '--binder', $BinderFile
            ))
        }
    }
    # One `collate` over all four copies. The plant's disagreements make this
    # exit 4 (escalation outranks re-read in `collate`'s own exit-code
    # contract) rather than 0, so this is the one stage `-Expect`s something
    # else.
    collate = {
        Invoke-Checked -Stage 'collate' -Expect 4 -CommandLine ($Launcher + @(
            $Cmd.collate, '--stage', '4', '--binder', $BinderFile, '--topology', $TopologyFile,
            '--edit-copy', $CopyFile['ownership-context'],
            '--edit-copy', $CopyFile['block-context'],
            '--edit-copy', $CopyFile['function-context'],
            '--edit-copy', $CopyFile['module-context'],
            '--out', $ChiefFile, '--proof-out', $Proof0File
        ))
    }
    # The chief's dispositions close the four carried-forward places
    # (`write_texts` plants them, matching the "the chief" column of the
    # scenario matrix), then `disposition` folds them into the closed proof.
    disposition = {
        Invoke-Checked -Stage 'plant-dispositions' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_texts; write_texts(Path(sys.argv[1]))',
            $Run
        )
        Invoke-Checked -Stage 'disposition' -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $Proof0File, '--binder', $BinderFile,
            '--dispositions', $DispositionsFile, '--out', $ChiefFinalFile,
            '--proof-out', $FinalFile
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

# Created here, after every refusal above, at the point its existence is
# checked, rather than checked with Test-Path and created later -- so
# nothing can be written into $Run between the check and the creation by
# two runs racing on the same name, and no refusal above leaves an empty
# $Run behind.
try {
    New-Item -ItemType Directory -Path $Run -ErrorAction Stop | Out-Null
} catch [System.IO.IOException] {
    if ($_.FullyQualifiedErrorId -eq 'DirectoryExist,Microsoft.PowerShell.Commands.NewItemCommand') {
        Write-Host "run directory already exists: $Run"
        exit 1
    }
    throw
}

try {
    Set-Location $RepoRoot

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
