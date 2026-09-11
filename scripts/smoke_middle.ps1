# Drives the middle stages of the comment-review chain over a fixture tree,
# for a smoke check that the chain from gather through proof still
# composes: a binder, a topology, seeded copies, a planted scenario matrix
# of marks, the fold's proof, the chief's dispositions closing it, and the
# revise `proof` pulls from the closed copy. The last stage diffs that
# revise against the text smoke_fixture.py says the plant makes land, and
# passes only when the two are identical.
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
    # PowerShell expands a leading ~ only in a path it resolves itself, and
    # GetFullPath would read it as a directory named ~.
    if ($Run -match '^~(?=$|[\\/])') {
        $Run = $HOME + $Run.Substring(1)
    }
    # GetFullPath refuses a base that is not a directory, so a relative -Run
    # from a registry or other non-filesystem location is refused here.
    if ([System.IO.Path]::IsPathFullyQualified($Run)) {
        $Run = [System.IO.Path]::GetFullPath($Run)
    } elseif ($CallerLocation.Provider.Name -eq 'FileSystem') {
        $Run = [System.IO.Path]::GetFullPath($Run, $CallerLocation.ProviderPath)
    } else {
        Write-Host "-Run is relative and the current location is not a directory: $Run"
        exit 1
    }
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
# (0 unless -Expect says otherwise). With -Capture it returns the
# command's standard output to the caller instead, for the one call whose
# output the script reads. On failure -- a wrong exit code or a missing
# executable -- it stops the script, printing any captured output, then
# running -OnFailure if given, then the stage name, the expected and
# actual exit codes, the directory it ran from and a command line that
# runs when pasted into PowerShell, so the failure carries its own
# reproduction. $PSNativeCommandUseErrorActionPreference is off above, so
# nothing but this function reports a native failure.
function Invoke-Checked {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [string[]]$CommandLine,
        [int]$Expect = 0,
        [switch]$Capture,
        [scriptblock]$OnFailure
    )
    $exe = $CommandLine[0]
    $rest = @($CommandLine | Select-Object -Skip 1)
    $captured = @()
    try {
        if ($Capture) {
            $captured = @(& $exe @rest)
        } else {
            & $exe @rest | Out-Host
        }
    } catch [System.Management.Automation.CommandNotFoundException] {
        Write-Host "stage failed: $Stage"
        Write-Host "executable not found: $exe"
        Write-Host "directory: $((Get-Location).Path)"
        Write-Host "command: $(Format-CommandLine $CommandLine)"
        exit 1
    }
    # Held before -OnFailure runs, since a native command it runs sets
    # $LASTEXITCODE again.
    $actual = $LASTEXITCODE
    if ($actual -ne $Expect) {
        $captured | Out-Host
        if ($OnFailure) {
            & $OnFailure
        }
        Write-Host "stage failed: $Stage"
        Write-Host "expected exit code: $Expect"
        Write-Host "actual exit code: $actual"
        Write-Host "directory: $((Get-Location).Path)"
        Write-Host "command: $(Format-CommandLine $CommandLine)"
        if ($actual -ne 0) {
            exit $actual
        }
        exit 1
    }
    if ($Capture) {
        return $captured
    }
}

$OriginalDir = Join-Path $Run 'original'
$FixtureFile = Join-Path $OriginalDir 'fib.py'
$BinderFile = Join-Path $Run 'binder.json'
$TopologyFile = Join-Path $Run 'topology.toml'
$CopiesDir = Join-Path $Run 'copies'

# The four roles stage 4 dispatches to. The distribute stage fills $CopyFile
# with the copy distribute wrote for each.
$Roles = @('ownership-context', 'block-context', 'function-context', 'module-context')
$CopyFile = @{}

$ChiefFile = Join-Path $Run 'chief.json'
$Proof0File = Join-Path $Run 'proof0.json'
$DispositionsFile = Join-Path $Run 'dispositions.json'
$ChiefFinalFile = Join-Path $Run 'chief-final.json'
$FinalFile = Join-Path $Run 'final.json'
$ProofDir = Join-Path $Run 'proof'
$ExpectedDir = Join-Path $Run 'expected'

# Each entry is one stage's work, and the chain as this script leaves it ends
# at diff. Add an entry to $Stages to extend it further, and a path variable
# above for anything the new stage writes.
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
            '--stage', ('4=' + ($Roles -join ','))
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
        # Each copy names its own role, so the copies are found by what they
        # hold rather than by the file names distribute gives them. The plant
        # marks one copy per role, so a role with none, or with more than one
        # -- a role stage 4 sharded -- stops the run here.
        $written = @(Get-ChildItem -LiteralPath $CopiesDir -File | ForEach-Object {
            [pscustomobject]@{
                Role = (Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json).role
                Path = $_.FullName
            }
        })
        foreach ($role in $Roles) {
            $held = @($written | Where-Object Role -EQ $role)
            if ($held.Count -ne 1) {
                Write-Host 'stage failed: distribute-4'
                Write-Host "copies for ${role}: $($held.Count), where the plant marks one"
                Write-Host "directory: $CopiesDir"
                exit 1
            }
            $CopyFile[$role] = $held[0].Path
        }
    }
    # `docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`'s
    # "The scenario matrix" named the first nine of these places, and the
    # addresser row's at the end; the plant goes five further -- one `mark`
    # invocation per ruling per role, no bulk pass, since `mark` itself
    # refuses one. A place three roles have nothing to add to is marked
    # clean by all three, or queried outside their remit; a2, b8, b17, c3
    # and the addresser row's place get a ruling from one role alone.
    mark = {
        Invoke-Checked -Stage 'plant-texts' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_texts; write_texts(Path(sys.argv[1]))',
            $Run
        )
        # One file per address `smoke_fixture.LANDINGS` gives text that a
        # `mark` call below plants -- written above by `write_texts`, named
        # here to match its own naming rather than read back from it. c6
        # and c1 are corrections, so each names two files: its false clause
        # and its true clause. The addresser row's file is not here: it is
        # named at that row from the address `addresser` returns.
        $LandingFile = @{
            c6_false = Join-Path $Run 'c6-false.txt'
            c6_true = Join-Path $Run 'c6-true.txt'
            c1_false = Join-Path $Run 'c1-false.txt'
            c1_true = Join-Path $Run 'c1-true.txt'
            b0 = Join-Path $Run 'b0.txt'
            a2 = Join-Path $Run 'a2.txt'
            b8 = Join-Path $Run 'b8.txt'
            b17 = Join-Path $Run 'b17.txt'
            c3 = Join-Path $Run 'c3.txt'
            c12 = Join-Path $Run 'c12.txt'
            a0 = Join-Path $Run 'a0.txt'
        }
        # a0 -- the module docstring, already filled. block-context adds over
        # it instead of cleaning it, to see what an add on a filled a does;
        # the other three clean it as before.
        Invoke-Checked -Stage 'mark a0 block-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@a0',
            '--instruction', 'add',
            '--missing', 'nothing states why the recursion is counted',
            '--anchor', '`__doc__`', '--anchor-line', '<module>',
            '--change', "@$($LandingFile.a0)",
            '--reason', 'the module docstring says what it counts but not what for',
            '--cite', 'fib.py:1', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark a0 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@a0',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # c12 -- beside `if n < 2:`, already filled with `# base case`.
        # ownership-context adds over it instead of cleaning it, to see what
        # an add on a filled c does; the other three clean it as before.
        Invoke-Checked -Stage 'mark c12 ownership-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'fib.py@c12',
            '--instruction', 'add',
            '--missing', 'nothing notes which values are already fibonacci numbers',
            '--anchor', '`n < 2`', '--anchor-line', '    if n < 2:',
            '--change', "@$($LandingFile.c12)",
            '--reason', 'the base case deserves saying why it needs no recursion',
            '--cite', 'fib.py:27', '--repo', $OriginalDir
        ))
        foreach ($role in @('block-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark c12 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@c12',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # b8 -- the empty gap above `return wrapper`, absent b. block-context
        # is the only role that touches this empty place.
        Invoke-Checked -Stage 'mark b8 block-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@b8',
            '--instruction', 'add',
            '--missing', 'nothing notes that counting is finished before wrapper returns',
            '--anchor', '`return wrapper`', '--anchor-line', '    return wrapper',
            '--change', "@$($LandingFile.b8)",
            '--reason', 'the return is the last step and nothing says so',
            '--cite', 'fib.py:18', '--repo', $OriginalDir
        ))
        # b17 -- the empty closing gap after the dunder-main block, absent b
        # at the foot (Addressing #19's foot rule). module-context is the
        # only role that touches this empty place.
        Invoke-Checked -Stage 'mark b17 module-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'fib.py@b17',
            '--instruction', 'add',
            '--missing', 'nothing notes that the module has nothing left to do here',
            '--anchor', '`__main__`', '--anchor-line', '<eof>',
            '--change', "@$($LandingFile.b17)",
            '--reason', 'the module ends here and nothing says so',
            '--cite', 'fib.py:34', '--repo', $OriginalDir
        ))
        # c3 -- the empty room beside `@functools.wraps(fn)`, absent c.
        # function-context is the only role that touches this empty place.
        Invoke-Checked -Stage 'mark c3 function-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@c3',
            '--instruction', 'add',
            '--missing', "nothing notes that wraps preserves fn's identity",
            '--anchor', '`functools.wraps`', '--anchor-line', '    @functools.wraps(fn)',
            '--change', "@$($LandingFile.c3)",
            '--reason', 'the decorator is why wrapper still looks like fn',
            '--cite', 'fib.py:12', '--repo', $OriginalDir
        ))
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
            '--false', "@$($LandingFile.c6_false)", '--true', "@$($LandingFile.c6_true)",
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
        # clause to different text, both reading that clause from one file;
        # ownership-context and module-context clean.
        Invoke-Checked -Stage 'mark c1 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@c1',
            '--instruction', 'correct',
            '--false', "@$($LandingFile.c1_false)", '--true', "@$($LandingFile.c1_true)",
            '--reason', 'the fixture calls this a cache everywhere else',
            '--cite', 'fib.py:6', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark c1 function-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@c1',
            '--instruction', 'correct',
            '--false', "@$($LandingFile.c1_false)", '--true', 'computed or not',
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
            '--change', "@$($LandingFile.b0)",
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
        # a2 -- one of seven adds. function-context is the only role that
        # touches this empty place; wrapper carries no slot in anyone
        # else's copy to rule on.
        Invoke-Checked -Stage 'mark a2 function-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@a2',
            '--instruction', 'add',
            '--missing', 'wrapper has no docstring', '--anchor', '`wrapper`',
            '--anchor-line', '    def wrapper(n):',
            '--change', "@$($LandingFile.a2)",
            '--reason', 'wrapper is the declared function; logged only wraps it',
            '--cite', 'fib.py:13', '--repo', $OriginalDir
        ))
        # The addresser row -- one add whose address this script does not
        # spell. `addresser` names the `b` place at line 33, the empty gap
        # above the dunder-main block, from the page itself, and prints one
        # tab-separated line: the address, the line of code as Python's
        # repr quotes it, and whether the binder holds the place. Only the
        # first two fields are read. module-context is the only role that
        # touches this empty place.
        $row = Get-Content -LiteralPath (Join-Path $Run 'addresser-row.json') -Raw | ConvertFrom-Json
        $addresserCommand = $Launcher + @(
            $Cmd.addresser, '--binder', $BinderFile, '--file', 'fib.py',
            '--line', $row.line, '--series', 'b'
        )
        $found = Invoke-Checked -Stage 'addresser' -Capture -CommandLine $addresserCommand
        $fields = @($found)[0] -split "`t"
        $addedAddress = $fields[0]
        if ($addedAddress -cne $row.address) {
            Write-Host 'stage failed: addresser'
            Write-Host "planted address: $($row.address)"
            Write-Host "addresser returned: $addedAddress"
            Write-Host "directory: $((Get-Location).Path)"
            Write-Host "command: $(Format-CommandLine $addresserCommand)"
            exit 1
        }
        # The repr's enclosing quotes are its only escaping on this line,
        # which holds no single quote and no backslash.
        $addedAnchorLine = $fields[1].Substring(1, $fields[1].Length - 2)
        # `write_texts` names an add's file after its address's cue.
        $addedFile = Join-Path $Run ($addedAddress.Split('@')[1] + '.txt')
        Invoke-Checked -Stage "mark $addedAddress module-context add" -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', $addedAddress,
            '--instruction', 'add',
            '--missing', 'nothing says what running the module directly does',
            '--anchor', '`__name__`', '--anchor-line', $addedAnchorLine,
            '--change', "@$addedFile",
            '--reason', 'the entry point is where a reader looks to see how it runs',
            '--cite', "fib.py:$($row.line)", '--repo', $OriginalDir
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
        $copies = foreach ($role in $Roles) { '--edit-copy', $CopyFile[$role] }
        Invoke-Checked -Stage 'collate' -Expect 4 -CommandLine ($Launcher + @(
            $Cmd.collate, '--stage', '4', '--binder', $BinderFile, '--topology', $TopologyFile
        ) + $copies + @(
            '--out', $ChiefFile, '--proof-out', $Proof0File
        ))
    }
    # The chief's dispositions close the ten carried-forward places
    # (`write_texts` writes `dispositions.json` at the mark stage above,
    # from `DISPOSITIONS` in smoke_fixture.py, which reads `b9`'s recast
    # prose out of `LANDINGS`), then `disposition` folds them into the
    # closed proof.
    disposition = {
        Invoke-Checked -Stage 'disposition' -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $Proof0File, '--binder', $BinderFile,
            '--dispositions', $DispositionsFile, '--out', $ChiefFinalFile,
            '--proof-out', $FinalFile
        ))
    }
    # `proof` pulls the closed chief copy into a revise of the original tree
    # at $ProofDir, which must not exist yet. Its code check refuses the
    # docstring a2 adds where wrapper had none, so a run stops here until
    # TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md is settled.
    proof = {
        Invoke-Checked -Stage 'proof' -CommandLine ($Launcher + @(
            $Cmd.proof, '--copy', $ChiefFinalFile, '--repo', $OriginalDir,
            '--out', $ProofDir
        ))
    }
    # The diff is the assertion: `write_expected` writes the text
    # smoke_fixture.py says the plant makes land, and git compares it with
    # the proof. Exit 0 means the proof is exactly what was planted. On a
    # difference it also prints the original against the proof, so a reader
    # sees what the chain did.
    diff = {
        New-Item -ItemType Directory -Path $ExpectedDir | Out-Null
        Invoke-Checked -Stage 'expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_expected; write_expected(Path(sys.argv[1]))',
            $ExpectedDir
        )
        Invoke-Checked -Stage 'diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $ExpectedDir, $ProofDir
        ) -OnFailure {
            Write-Host 'what the chain did -- the original against the proof:'
            & git -c core.autocrlf=false --no-pager diff --no-index -- $OriginalDir $ProofDir | Out-Host
        }
    }
}

# $PSBoundParameters tells "not given" (run every stage) from "given
# empty" (refused), which $Stop alone cannot: both read as falsy.
if ($PSBoundParameters.ContainsKey('Stop') -and
    ($Stop -eq '' -or $Stages.Keys -notcontains $Stop)) {
    Write-Host "unknown -Stop value: '$Stop' (valid: $($Stages.Keys -join ', '))"
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

# An in-process caller reads $LASTEXITCODE, which still holds the last native
# command's code -- collate's expected 4, for a run stopped there.
exit 0
