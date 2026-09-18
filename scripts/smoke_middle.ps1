# Drives the middle stages of the comment-review chain over a fixture tree,
# for a smoke check that the chain from gather through proof still
# composes: a binder, a topology, seeded copies, the planted marks, the
# fold's proof, one turn in which every role answers what the fold carried
# forward, the chief's dispositions closing what the turn still carries
# forward, the docket `proof` transcribes from the closed copy, and the
# revise `proof` pulls from that docket. The diff stage compares that revise
# with the text smoke_fixture.py says the plant makes land, and passes
# only when the two are identical. The last stage runs a second editorial
# stage over that revise -- the topology says it reads it -- and diffs its
# proof the same way.
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
    mark = 'mark'; check = 'check'; collate = 'collate'; turn = 'turn'
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
    # GetFullPath throws on a base that is not a fully qualified path, and a
    # registry or other non-filesystem location has none, so a relative -Run
    # from one is refused and an absolute one is resolved without a base.
    if ([System.IO.Path]::IsPathFullyQualified($Run)) {
        $Run = [System.IO.Path]::GetFullPath($Run)
    } elseif ($CallerLocation.Provider.Name -eq 'FileSystem') {
        $Run = [System.IO.Path]::GetFullPath($Run, $CallerLocation.ProviderPath)
    } else {
        Write-Host "-Run is relative and the current location is not a directory: $Run"
        exit 1
    }
}

# A run leaves no permanent code changes inside the repo, and its outputs
# belong outside it, so a -Run landing there is refused before any work is
# done.
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
# still runs -- a quoted path followed by arguments is a parse error
# without the call operator.
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

# Runs one native command and checks its exit code against what the stage
# expects (0 unless -Expect says otherwise). The command's output goes to
# the host (Out-Host), so an in-process caller capturing this script's
# output gets only what the script Write-Outputs; under pwsh -File the
# host writes to stdout, so a caller capturing that process gets both.
# With -Capture it returns the command's standard output instead, for the
# calls whose output the script reads, and -AndErrors merges the command's
# standard error into what comes back -- a command that prints its refusals
# there, as `distribute` does, says nothing on stdout to assert against.
#
# A wrong exit code stops the script: it prints any captured output, runs
# -OnFailure if given, then prints the stage name, the expected and actual
# exit codes, the directory it ran from and a command line that runs when
# pasted into PowerShell, and exits with the actual code, or 1 where that
# is 0. A missing executable stops it too, printing the stage name, the
# executable, the directory and the command line, and exiting 1.
# $PSNativeCommandUseErrorActionPreference is off above, so nothing but
# this function reports a native failure.
function Invoke-Checked {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [string[]]$CommandLine,
        [int]$Expect = 0,
        [switch]$Capture,
        [switch]$AndErrors,
        [scriptblock]$OnFailure
    )
    $exe = $CommandLine[0]
    $rest = @($CommandLine | Select-Object -Skip 1)
    $captured = @()
    try {
        if ($Capture -and $AndErrors) {
            $captured = @(& $exe @rest 2>&1 | ForEach-Object { $_.ToString() })
        } elseif ($Capture) {
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
$RateFile = Join-Path $OriginalDir 'rate.py'
$StoreFile = Join-Path $OriginalDir 'store.py'
$BinderFile = Join-Path $Run 'binder.json'
$TopologyFile = Join-Path $Run 'topology.toml'
$CopiesDir = Join-Path $Run 'copies'

# The four roles stage 4 dispatches to. The distribute stage fills $CopyFile
# with the copy distribute wrote for each.
$Roles = @('ownership-context', 'block-context', 'function-context', 'module-context')
$CopyFile = @{}

$ChiefFile = Join-Path $Run 'chief.json'
$Proof0File = Join-Path $Run 'proof0.json'
$Batch1File = Join-Path $Run 'batch1.json'
$Proof1File = Join-Path $Run 'proof1.json'
$Batch2File = Join-Path $Run 'batch2.json'
$DispositionsFile = Join-Path $Run 'dispositions.json'
$ChiefFinalFile = Join-Path $Run 'chief-final.json'
$FinalFile = Join-Path $Run 'final.json'
$DocketFile = Join-Path $Run 'docket.json'
$ProofDir = Join-Path $Run 'proof'
$ExpectedDir = Join-Path $Run 'expected'
$RoleDraftDir = Join-Path $Run 'role-draft'
$RoleExpectedDir = Join-Path $Run 'role-expected'
$CollideCopyFile = Join-Path $Run 'collide-copy.json'
$ParityCopyFile = Join-Path $Run 'parity-copy.json'
$WrapCopiesDir = Join-Path $Run 'wrap-copies'
$WrapDraftDir = Join-Path $Run 'wrap-draft'
$WrapExpectedDir = Join-Path $Run 'wrap-expected'
$CollideDraftDir = Join-Path $Run 'collide-draft'
$CollideExpectedDir = Join-Path $Run 'collide-expected'

# The root refusal sub-plant (Process #178): a second tree holding the same
# fixture, a binder over it, and the copy distribute seeds from that binder.
# The three paths below it are what a refused collate must not write.
$OtherDir = Join-Path $Run 'other'
$OtherBinderFile = Join-Path $Run 'other-binder.json'
$OtherCopiesDir = Join-Path $Run 'other-copies'
$OtherChiefFile = Join-Path $Run 'other-chief.json'
$OtherProofFile = Join-Path $Run 'other-proof.json'
$OtherBatchFile = Join-Path $Run 'other-batch.json'

# The cite refusal sub-plant (Process #181), and what a refused turn must not
# write.
$BadCiteProofFile = Join-Path $Run 'bad-cite-proof.json'
$BadCiteBatchFile = Join-Path $Run 'bad-cite-batch.json'

# The second stage, whose topology row reads the revise the first stage's
# proof pulled. Its binder is gathered from $ProofDir, so the addresses it
# rules on are the revise's own.
$SecondStage = '5'
$SecondRole = 'ownership-context'
$SecondBinderFile = Join-Path $Run 'binder2.json'
$SecondCopiesDir = Join-Path $Run 'copies2'
$SecondChiefFile = Join-Path $Run 'chief2.json'
$SecondProofFile = Join-Path $Run 'proof2.json'
$SecondDocketFile = Join-Path $Run 'docket2.json'
$SecondProofDir = Join-Path $Run 'proof2'
$SecondExpectedDir = Join-Path $Run 'second-expected'

# The one-liner that writes the three fixture files into a directory, used by
# the fixture stage and by the second tree the root refusal sub-plant gathers.
$WriteFixtures = 'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_fixture, write_rate_fixture, write_store_fixture; root = Path(sys.argv[1]); write_fixture(root); write_rate_fixture(root); write_store_fixture(root)'

# Each entry is one stage's work, and the chain as this script leaves it ends
# at diff. Each block runs in its own scope, so a variable a stage assigns is
# gone when the next stage starts: what a later stage reads is a path above,
# or a table above that a stage fills in place, as distribute fills
# $CopyFile. Add an entry to $Stages to extend the chain, and a path
# variable above for anything the new stage writes.
$Stages = [ordered]@{
    fixture = {
        New-Item -ItemType Directory -Path $OriginalDir | Out-Null
        Invoke-Checked -Stage 'fixture' -CommandLine @(
            'uv', 'run', 'python', '-c',
            $WriteFixtures,
            $OriginalDir
        )
    }
    gather = {
        Invoke-Checked -Stage 'gather' -CommandLine ($Launcher + @(
            $Cmd.gather, '--repo', $OriginalDir, '--out', $BinderFile,
            $FixtureFile, $RateFile, $StoreFile
        ))
    }
    topology = {
        # Two stages: the four roles at once, then one role reading the revise
        # the first stage's proof pulls. `compose` writes the second stage's
        # `reads` as `revise:4`, which is what decides the tree the `second`
        # stage below is seeded from.
        Invoke-Checked -Stage 'topology-build' -CommandLine ($Launcher + @(
            $Cmd.topology, '--build', '--binder', $BinderFile, '--out', $TopologyFile,
            '--stage', ('4=' + ($Roles -join ',')),
            '--stage', ($SecondStage + '=' + $SecondRole)
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
    # One `mark` call per ruling per role: `mark` takes one ruling per call
    # and has no bulk pass. `LANDINGS` in smoke_fixture.py names what each
    # planted place makes land. An empty place is in no copy, since a copy
    # is seeded with the places that hold prose, so an add there creates its
    # slot in its own role's copy and no other role has one to rule on:
    # fib.py's a2, b8, b17 and c3 and the addresser row's place take one call
    # each. A row's comment names a fib.py place by its cue alone; the three
    # rate.py rows, last, name their page.
    mark = {
        Invoke-Checked -Stage 'plant-texts' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_texts; write_texts(Path(sys.argv[1]))',
            $Run
        )
        # One file per text a `mark` call below plants from
        # `smoke_fixture.LANDINGS` -- written above by `write_texts`, named
        # here to match its own naming rather than read back from it. A
        # correction names two files, its false clause and its true clause,
        # and so does the patch, its from clause and its to clause. Every
        # name carries the page as well as the cue, which is what
        # `smoke_fixture.file_for` spells. The addresser row's file is not
        # here: it is named at that row from the address `addresser` returns.
        $LandingFile = @{
            fib_c6_false = Join-Path $Run 'fib-c6-false.txt'
            fib_c6_true = Join-Path $Run 'fib-c6-true.txt'
            fib_c1_false = Join-Path $Run 'fib-c1-false.txt'
            fib_c1_true = Join-Path $Run 'fib-c1-true.txt'
            rate_c3_from = Join-Path $Run 'rate-c3-from.txt'
            rate_c3_to = Join-Path $Run 'rate-c3-to.txt'
            fib_b0 = Join-Path $Run 'fib-b0.txt'
            fib_a2 = Join-Path $Run 'fib-a2.txt'
            fib_b8 = Join-Path $Run 'fib-b8.txt'
            fib_b17 = Join-Path $Run 'fib-b17.txt'
            fib_c3 = Join-Path $Run 'fib-c3.txt'
            fib_c12 = Join-Path $Run 'fib-c12.txt'
            fib_a0 = Join-Path $Run 'fib-a0.txt'
            store_b1 = Join-Path $Run 'store-b1.txt'
            store_b3 = Join-Path $Run 'store-b3.txt'
            store_b8 = Join-Path $Run 'store-b8.txt'
            store_b7_false = Join-Path $Run 'store-b7-false.txt'
            store_b7_true = Join-Path $Run 'store-b7-true.txt'
            store_c5_false = Join-Path $Run 'store-c5-false.txt'
            store_c5_true = Join-Path $Run 'store-c5-true.txt'
        }
        # a0 -- the module docstring, already filled. block-context adds over
        # it: `--change` is the text it adds and `--raw-text` the docstring as
        # it will read, which keeps every word already there in order, so
        # `mark` accepts the add (Process #132 and #176); the other three
        # clean it.
        Invoke-Checked -Stage 'mark a0 block-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@a0',
            '--instruction', 'add',
            '--missing', 'nothing states why the recursion is counted',
            '--anchor', '`__doc__`', '--anchor-line', '<module>',
            '--change', 'and why it is counted',
            '--raw-text', "@$($LandingFile.fib_a0)",
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
        # ownership-context adds over it with a `--raw-text` that drops `base`
        # and `case`, and `mark` refuses it: an add at a place holding prose
        # reads with every word of that prose, in order (Process #132 and
        # #176). The refusal is asserted by its exit code and by the line
        # naming the place and the word dropped. The copy is left as it was, so
        # ownership-context then cleans c12 as the other three do.
        $c12Add = $Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'fib.py@c12',
            '--instruction', 'add',
            '--missing', 'nothing notes which values are already fibonacci numbers',
            '--anchor', '`n < 2`', '--anchor-line', '    if n < 2:',
            '--change', '0 and 1 are already fibonacci numbers',
            '--raw-text', "@$($LandingFile.fib_c12)",
            '--reason', 'the base case deserves saying why it needs no recursion',
            '--cite', 'fib.py:27', '--repo', $OriginalDir
        )
        $refused = Invoke-Checked -Stage 'mark c12 ownership-context add refused' -Expect 1 -Capture -CommandLine $c12Add
        if (-not (($refused -join "`n").Contains("fib.py@c12: the text does not keep 'base'"))) {
            Write-Host 'stage failed: mark c12 ownership-context add refused'
            Write-Host 'expected a refusal naming fib.py@c12 and the word it drops; mark printed:'
            $refused | Out-Host
            Write-Host "directory: $((Get-Location).Path)"
            Write-Host "command: $(Format-CommandLine $c12Add)"
            exit 1
        }
        foreach ($role in $Roles) {
            Invoke-Checked -Stage "mark c12 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@c12',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # b8 -- the empty gap above `return wrapper`, absent b.
        Invoke-Checked -Stage 'mark b8 block-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@b8',
            '--instruction', 'add',
            '--missing', 'nothing notes that counting is finished before wrapper returns',
            '--anchor', '`return wrapper`', '--anchor-line', '    return wrapper',
            '--change', "@$($LandingFile.fib_b8)",
            '--reason', 'the return is the last step and nothing says so',
            '--cite', 'fib.py:18', '--repo', $OriginalDir
        ))
        # b17 -- the empty closing gap after the dunder-main block, absent b.
        Invoke-Checked -Stage 'mark b17 module-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'fib.py@b17',
            '--instruction', 'add',
            '--missing', 'nothing notes that the module has nothing left to do here',
            '--anchor', '`__main__`', '--anchor-line', '<eof>',
            '--change', "@$($LandingFile.fib_b17)",
            '--reason', 'the module ends here and nothing says so',
            '--cite', 'fib.py:34', '--repo', $OriginalDir
        ))
        # c3 -- the empty room beside `@functools.wraps(fn)`, absent c.
        Invoke-Checked -Stage 'mark c3 function-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@c3',
            '--instruction', 'add',
            '--missing', "nothing notes that wraps preserves fn's identity",
            '--anchor', '`functools.wraps`', '--anchor-line', '    @functools.wraps(fn)',
            '--change', "@$($LandingFile.fib_c3)",
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
        # The true clause is spelled `--true=@path`, which argparse reads as it
        # reads `--true @path`: mark reads the file either way, and the literal
        # path never lands in the claim (mark-defects T23, smoke T5).
        Invoke-Checked -Stage 'mark c6 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@c6',
            '--instruction', 'correct',
            '--false', "@$($LandingFile.fib_c6_false)", "--true=@$($LandingFile.fib_c6_true)",
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
            '--false', "@$($LandingFile.fib_c1_false)", '--true', "@$($LandingFile.fib_c1_true)",
            '--reason', 'the fixture calls this a cache everywhere else',
            '--cite', 'fib.py:6', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark c1 function-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@c1',
            '--instruction', 'correct',
            '--false', "@$($LandingFile.fib_c1_false)", '--true', 'computed or not',
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
        # smoke T7: block-context places a first ruling at b9, takes it back
        # with --withdraw, and places the one that lands below -- the copy
        # holds only the second (mark-defects T24).
        Invoke-Checked -Stage 'mark b9 block-context first correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@b9',
            '--instruction', 'correct',
            '--false', 'logged sees', '--true', 'logged looks at',
            '--reason', 'a first reading, taken back below',
            '--cite', 'fib.py:21', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark b9 block-context withdraw' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@b9',
            '--withdraw'
        ))
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
        # defer with a scope-declaring query rather than clean. The whole
        # paragraph leaves, so the snippet `--change` subtracts from b1 and the
        # `--raw-text` b0 reads with are the same text (Process #172 and #175).
        Invoke-Checked -Stage 'mark b1 ownership-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'fib.py@b1',
            '--instruction', 'move', '--from', 'fib.py@b1', '--to', 'fib.py@b0',
            '--change', "@$($LandingFile.fib_b0)", '--raw-text', "@$($LandingFile.fib_b0)",
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
        # Two moves mark refuses and writes nothing for, so the copy the fold
        # reads is unchanged: one out of the code, which is not carried yet and
        # is routed to a human-review query (Process #173, smoke T4), and one
        # to a bare cue, which names a place on no page (smoke T5).
        $outOfCode = $Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'fib.py@b9',
            '--instruction', 'move', '--from', 'fib.py@b9', '--to', 'docs/history.md',
            '--change', '# The cache sits inside the decorator stack on purpose.',
            '--raw-text', '# The cache sits inside the decorator stack on purpose.',
            '--reason', 'why the stack is ordered is history, not a rule for this code',
            '--cite', 'fib.py:21', '--repo', $OriginalDir
        )
        $refused = Invoke-Checked -Stage 'mark b9 module-context move out of the code refused' -Expect 1 -Capture -CommandLine $outOfCode
        if (-not (($refused -join "`n").Contains('human-review-necessary'))) {
            Write-Host 'stage failed: mark b9 module-context move out of the code refused'
            Write-Host 'expected a refusal routing the role to a human-review query; mark printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $outOfCode)"
            exit 1
        }
        $bareCue = $Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'fib.py@b1',
            '--instruction', 'move', '--from', 'fib.py@b1', '--to', 'b0',
            '--change', '# Module state, written by the wrapper and read by the caller.',
            '--raw-text', '# Module state, written by the wrapper and read by the caller.',
            '--reason', 'module state belongs above the import',
            '--cite', 'fib.py:5', '--repo', $OriginalDir
        )
        $refused = Invoke-Checked -Stage 'mark b1 module-context move to a bare cue refused' -Expect 1 -Capture -CommandLine $bareCue
        if (-not (($refused -join "`n").Contains('`path@cue`'))) {
            Write-Host 'stage failed: mark b1 module-context move to a bare cue refused'
            Write-Host 'expected a refusal naming the path@cue form; mark printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $bareCue)"
            exit 1
        }
        # a2 -- the empty place for wrapper's docstring, absent a.
        Invoke-Checked -Stage 'mark a2 function-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@a2',
            '--instruction', 'add',
            '--missing', 'wrapper has no docstring', '--anchor', '`wrapper`',
            '--anchor-line', '    def wrapper(n):',
            '--change', "@$($LandingFile.fib_a2)",
            '--reason', 'wrapper is the declared function; logged only wraps it',
            '--cite', 'fib.py:13', '--repo', $OriginalDir
        ))
        # The addresser row -- one add whose address this script does not
        # spell. It asks `addresser` for the `b` place at the line
        # `write_texts` put in addresser-row.json, and stops unless the
        # address that comes back is the one beside it there. `addresser`
        # prints one tab-separated line: the address, the line of code as
        # Python's repr quotes it, and whether the binder holds the place.
        # Only the first two fields are read.
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
        # `write_texts` names an add's file after its address's page and cue,
        # which `smoke_fixture.file_for` spells and this composes to match.
        $addedParts = $addedAddress.Split('@')
        $addedFile = Join-Path $Run ([System.IO.Path]::GetFileNameWithoutExtension($addedParts[0]) + '-' + $addedParts[1] + '.txt')
        Invoke-Checked -Stage "mark $addedAddress module-context add" -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', $addedAddress,
            '--instruction', 'add',
            '--missing', 'nothing says what running the module directly does',
            '--anchor', '`__name__`', '--anchor-line', $addedAnchorLine,
            '--change', "@$addedFile",
            '--reason', 'the entry point is where a reader looks to see how it runs',
            '--cite', "fib.py:$($row.line)", '--repo', $OriginalDir
        ))
        # rate.py@b1 -- the composition. block-context corrects the first
        # sentence on the paragraph's first line and function-context the
        # second on its last; the line between is untouched, so the two
        # edits meet on no line and collate composes them. ownership-context
        # and module-context clean.
        Invoke-Checked -Stage 'mark rate.py@b1 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'rate.py@b1',
            '--instruction', 'correct',
            '--false', 'Zero calls give', '--true', 'No calls give',
            '--reason', 'the guard tests for no calls at all, not for a count',
            '--cite', 'rate.py:5', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark rate.py@b1 function-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'rate.py@b1',
            '--instruction', 'correct',
            '--false', 'never above one', '--true', 'never more than one',
            '--reason', 'more than names the comparison the division is bounded by',
            '--cite', 'rate.py:7', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'module-context')) {
            Invoke-Checked -Stage "mark rate.py@b1 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'rate.py@b1',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # rate.py@c3 -- the patch. module-context rewords the trailing
        # comment and cites nothing, since a patch owes no source.
        # function-context cannot tell whether the wording wants changing and
        # defers with an unable-to-determine query; ownership-context and
        # block-context defer with a scope-declaring query. A query of either
        # shape abstains, so the fold settles the patch alone.
        Invoke-Checked -Stage 'mark rate.py@c3 module-context patch' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'rate.py@c3',
            '--instruction', 'patch',
            '--from', "@$($LandingFile.rate_c3_from)", '--to', "@$($LandingFile.rate_c3_to)",
            '--reason', 'fraction names the ratio the division returns'
        ))
        Invoke-Checked -Stage 'mark rate.py@c3 function-context query' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'rate.py@c3',
            '--instruction', 'query', '--shape', 'unable-to-determine',
            '--attempted', 'read the comment against the division on its line',
            '--settles', 'another role',
            '--reason', 'the code does not say which word for the ratio is wanted',
            '--cite', 'rate.py:7', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'block-context')) {
            Invoke-Checked -Stage "mark rate.py@c3 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'rate.py@c3',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'module-context',
                '--reason', "this paragraph's subject is the wording of one comment, not my remit",
                '--cite', 'rate.py:7', '--repo', $OriginalDir
            ))
        }
        # rate.py@b5 -- the drop of a place that owns a leading, the blank
        # line below it. block-context drops share's comment; the other three
        # defer with a scope-declaring query rather than clean.
        Invoke-Checked -Stage 'mark rate.py@b5 block-context drop' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'rate.py@b5',
            '--instruction', 'drop',
            '--drop', '    # Kept for callers that ask for a share rather than a rate.',
            '--reason', "share's one line already says it hands the call to rate",
            '--cite', 'rate.py:13', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark rate.py@b5 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'rate.py@b5',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'block-context',
                '--reason', "this paragraph's subject is what share's body already says, not my remit",
                '--cite', 'rate.py:13', '--repo', $OriginalDir
            ))
        }
        # store.py@b1 -- the partial move, to store.py@b3. ownership-context
        # takes the paragraph's second sentence: `--change` is that snippet,
        # subtracted from b1 exactly once, and `--raw-text` is b3's paragraph
        # as it will read with the snippet on a line of its own (Process #172
        # and #175). The origin keeps its first sentence where a whole-
        # paragraph move would have emptied it. The other three roles defer
        # with a scope-declaring query.
        Invoke-Checked -Stage 'mark store.py@b1 ownership-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'store.py@b1',
            '--instruction', 'move', '--from', 'store.py@b1', '--to', 'store.py@b3',
            '--change', "@$($LandingFile.store_b1)", '--raw-text', "@$($LandingFile.store_b3)",
            '--reason', 'what is never removed is a fact about a miss, not about a lookup',
            '--cite', 'store.py:2', '--repo', $OriginalDir
        ))
        foreach ($role in @('block-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark store.py@b1 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'store.py@b1',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'ownership-context',
                '--reason', "this paragraph's subject is which function a sentence belongs to, not my remit",
                '--cite', 'store.py:2', '--repo', $OriginalDir
            ))
        }
        # store.py@b3 -- where that snippet arrives. ownership-context was
        # handed a slot here as well as at the origin, and reports nothing
        # about the paragraph itself; the move is what rules the place. The
        # other three defer.
        Invoke-Checked -Stage 'mark store.py@b3 ownership-context clean' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', 'store.py@b3',
            '--instruction', 'clean', '--repo', $OriginalDir
        ))
        foreach ($role in @('block-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark store.py@b3 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'store.py@b3',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'ownership-context',
                '--reason', "this paragraph's subject is which function a sentence belongs to, not my remit",
                '--cite', 'store.py:7', '--repo', $OriginalDir
            ))
        }
        # store.py@b5 -- the move a role holds for the human. module-context
        # moves the whole paragraph to store.py@b8, the closing gap, so its
        # `--change` and its `--raw-text` are one text; block-context reads
        # the same place and marks a human-review query. Both ends of the
        # move then ride to the end unruled and print as one entry naming
        # both (Process #182). The other two roles defer.
        Invoke-Checked -Stage 'mark store.py@b5 module-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'store.py@b5',
            '--instruction', 'move', '--from', 'store.py@b5', '--to', 'store.py@b8',
            '--change', "@$($LandingFile.store_b8)", '--raw-text', "@$($LandingFile.store_b8)",
            '--reason', 'rounding is the last thing the module does and reads as its closing note',
            '--cite', 'store.py:12', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark store.py@b5 block-context query' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'store.py@b5',
            '--instruction', 'query', '--shape', 'human-review-necessary',
            '--attempted', 'read the comment against the rounding on the line below it',
            '--settles', 'human',
            '--reason', 'whether this note belongs beside the code or at the foot is the author''s call',
            '--cite', 'store.py:12', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context')) {
            Invoke-Checked -Stage "mark store.py@b5 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'store.py@b5',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'block-context',
                '--reason', "this paragraph's subject is where a note sits on the page, not my remit",
                '--cite', 'store.py:12', '--repo', $OriginalDir
            ))
        }
        # store.py@b7 -- the lone proposal against cleans. module-context
        # corrects; the other three clean rather than defer, so the corrected
        # text is one none of them has seen and collate carries the place
        # forward to exactly those three as a composition (Process #180).
        # Their `clean` answers in the turn settle it.
        Invoke-Checked -Stage 'mark store.py@b7 module-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'store.py@b7',
            '--instruction', 'correct',
            '--false', "@$($LandingFile.store_b7_false)", '--true', "@$($LandingFile.store_b7_true)",
            '--reason', 'the guard tests the count, which is not the same as nothing having happened',
            '--cite', 'store.py:18', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'block-context', 'function-context')) {
            Invoke-Checked -Stage "mark store.py@b7 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'store.py@b7',
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
        }
        # store.py@c5 -- the correct whose change is wider than its claim.
        # block-context writes the change itself rather than leaving `mark` to
        # derive it from the clauses, and it drops `wants`, a word the claim
        # never names. The fold reports that under its own heading for the
        # chief and rolls nothing back for it (Process #177), so the change
        # lands. The other three roles defer.
        Invoke-Checked -Stage 'mark store.py@c5 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'store.py@c5',
            '--instruction', 'correct',
            '--false', "@$($LandingFile.store_c5_false)", '--true', "@$($LandingFile.store_c5_true)",
            '--change', '  # two decimal places, as the report asks',
            '--reason', 'round(x, 2) keeps two decimal places, which two places alone does not say',
            '--cite', 'store.py:13', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark store.py@c5 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'store.py@c5',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the comment against the rounding on its line',
                '--settles', 'block-context',
                '--reason', 'what round(x, 2) keeps is the block below me, not my remit',
                '--cite', 'store.py:13', '--repo', $OriginalDir
            ))
        }
    }
    # `check` over each of the four copies, before `collate`, whose exit code
    # cannot say the same: collate is expected to exit 4 below, and in its
    # exit codes an escalation outranks a place a role left unruled, so a
    # copy short of a ruling would still meet that expectation. `check`
    # exits 1 on it.
    check = {
        foreach ($role in $Roles) {
            Invoke-Checked -Stage "check $role" -CommandLine ($Launcher + @(
                $Cmd.check, '--edit-copy', $CopyFile[$role], '--binder', $BinderFile
            ))
        }
        # no-command-for-the-middle T99: check resolves a move's destination
        # against the real page, as collate does. A copy of module-context's
        # copy moves fib.py@b14 to fib.py@b99, a place fib.py does not carry;
        # mark takes it, since the form is right, and check names it.
        Copy-Item -LiteralPath $CopyFile['module-context'] -Destination $ParityCopyFile
        Invoke-Checked -Stage 'check parity mark' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $ParityCopyFile, '--address', 'fib.py@b14',
            '--instruction', 'move', '--from', 'fib.py@b14', '--to', 'fib.py@b99',
            '--change', '    # Two calls per level, which is what the counter measures.',
            '--raw-text', '    # Two calls per level, which is what the counter measures.',
            '--reason', 'the counting note belongs with the counter',
            '--cite', 'fib.py:29', '--repo', $OriginalDir
        ))
        $parity = $Launcher + @($Cmd.check, '--edit-copy', $ParityCopyFile, '--binder', $BinderFile)
        $named = Invoke-Checked -Stage 'check parity refused' -Expect 1 -Capture -CommandLine $parity
        if (-not (($named -join "`n").Contains("carries no place 'b99'"))) {
            Write-Host 'stage failed: check parity refused'
            Write-Host 'expected check to name fib.py@b99 as a place fib.py does not carry; check printed:'
            $named | Out-Host
            Write-Host "command: $(Format-CommandLine $parity)"
            exit 1
        }
    }
    # `proof --copy` over one role's own copy, before the fold -- the draft the
    # brief tells a role it may pull to read its marks as they would stand.
    # `write_role_draft` writes what smoke_fixture.py says that role's marks
    # make land, and git compares it with the draft: every place the role
    # marked clean or query keeps its prose (docket-defects T10).
    draft = {
        Invoke-Checked -Stage 'draft' -CommandLine ($Launcher + @(
            $Cmd.proof, '--copy', $CopyFile['function-context'], '--repo', $OriginalDir,
            '--out', $RoleDraftDir
        ))
        New-Item -ItemType Directory -Path $RoleExpectedDir | Out-Null
        Invoke-Checked -Stage 'draft-expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_role_draft; write_role_draft(Path(sys.argv[1]))',
            $RoleExpectedDir
        )
        Invoke-Checked -Stage 'draft-diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $RoleExpectedDir, $RoleDraftDir
        )
        # docket-defects T11, over a copy of that role's copy: a move from
        # rate.py@b5 into rate.py@b1, a place the role also corrected. It is a
        # copy so the fold still reads the role's own. Three `mark` calls at
        # the same move, differing only in the destination text, and each
        # refusal writes nothing -- so the copy the fold reads holds the one
        # that was placed.
        Copy-Item -LiteralPath $CopyFile['function-context'] -Destination $CollideCopyFile
        Invoke-Checked -Stage 'collide plant' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_collide_plant; write_collide_plant(Path(sys.argv[1]))',
            $Run
        )
        $collideMove = $Launcher + @(
            $Cmd.mark, '--edit-copy', $CollideCopyFile, '--address', 'rate.py@b5',
            '--instruction', 'move', '--from', 'rate.py@b5', '--to', 'rate.py@b1',
            '--change', '    # Kept for callers that ask for a share rather than a rate.',
            '--reason', "share's comment says what rate's does, and belongs with it",
            '--cite', 'rate.py:11', '--repo', $OriginalDir
        )
        # The moved comment alone as the destination text discards the
        # paragraph b1 already holds: the move's row reads the destination
        # against the page there (Process #175). Nothing else drives that
        # refusal through the console over a real page.
        $discards = $collideMove + @(
            '--raw-text', '    # Kept for callers that ask for a share rather than a rate.'
        )
        $refused = Invoke-Checked -Stage 'draft collide destination refused' -Expect 1 -Capture -CommandLine $discards
        if (-not (($refused -join "`n").Contains('the destination text does not keep'))) {
            Write-Host 'stage failed: draft collide destination refused'
            Write-Host 'expected a refusal naming what the destination text drops; mark printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $discards)"
            exit 1
        }
        # The same comment BELOW the paragraph keeps every word, so the row
        # takes it -- and the paragraph's last line carries no newline, so a
        # line after it rewrites that line, which is the line the role's own
        # correct rewrites. Two of one role's marks on one sentence do not
        # compose, and `mark` refuses at placing time what the fold would
        # refuse at the fold (Process #179).
        $sameSentence = $collideMove + @(
            '--raw-text', "@$(Join-Path $Run 'collide-same-sentence.txt')"
        )
        $refused = Invoke-Checked -Stage 'draft collide same sentence refused' -Expect 1 -Capture -CommandLine $sameSentence
        if (-not (($refused -join "`n").Contains('edit the same sentence and do not compose'))) {
            Write-Host 'stage failed: draft collide same sentence refused'
            Write-Host 'expected a refusal naming the two marks that do not compose; mark printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $sameSentence)"
            exit 1
        }
        # And the same comment ABOVE the paragraph edits no line the correct
        # edits, so the two compose into that role's one side and the draft
        # lands both: the moved comment arrives and the correction stands.
        # `write_collide_draft` writes what that makes of each page.
        Invoke-Checked -Stage 'draft collide mark' -CommandLine ($collideMove + @(
            '--raw-text', "@$(Join-Path $Run 'collide-raw-text.txt')"
        ))
        Invoke-Checked -Stage 'draft collide' -CommandLine ($Launcher + @(
            $Cmd.proof, '--copy', $CollideCopyFile, '--repo', $OriginalDir,
            '--out', $CollideDraftDir
        ))
        New-Item -ItemType Directory -Path $CollideExpectedDir | Out-Null
        Invoke-Checked -Stage 'draft collide expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_collide_draft; write_collide_draft(Path(sys.argv[1]))',
            $CollideExpectedDir
        )
        Invoke-Checked -Stage 'draft collide diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $CollideExpectedDir, $CollideDraftDir
        )
        # mark-defects T25, smoke T8: a drop across a line break joins the text
        # either side onto one line. Copies distributed again hold no rulings,
        # so ownership-context's fresh copy carries this one drop alone, and
        # its draft of rate.py is compared with smoke_fixture.py's
        # WRAP_RATE_DRAFT: the joined line rewrapped to b1's widest before it.
        Invoke-Checked -Stage 'wrap distribute' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--topology', $TopologyFile, '--stage', '4',
            '--binder', $BinderFile, '--out-dir', $WrapCopiesDir
        ))
        $wrapCopy = @(Get-ChildItem -LiteralPath $WrapCopiesDir -File | Where-Object {
            (Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json).role -eq 'ownership-context'
        })[0].FullName
        New-Item -ItemType Directory -Path $WrapExpectedDir | Out-Null
        Invoke-Checked -Stage 'wrap plant' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_wrap_plant; write_wrap_plant(Path(sys.argv[1]), Path(sys.argv[2]))',
            $Run, $WrapExpectedDir
        )
        Invoke-Checked -Stage 'wrap drop' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $wrapCopy, '--address', 'rate.py@b1',
            '--instruction', 'drop', '--drop', "@$(Join-Path $Run 'wrap-drop.txt')",
            '--reason', 'what the guard tests is said by the code below it',
            '--cite', 'rate.py:5', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'wrap draft' -CommandLine ($Launcher + @(
            $Cmd.proof, '--copy', $wrapCopy, '--repo', $OriginalDir, '--out', $WrapDraftDir
        ))
        Invoke-Checked -Stage 'wrap diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $WrapExpectedDir, $WrapDraftDir
        )
    }
    # One `collate` over all four copies, writing the master proof and the
    # turn's batch. The plant's disagreements make this exit 4 (escalation
    # outranks re-read in `collate`'s own exit-code contract) rather than 0;
    # `turn` below is the other stage that `-Expect`s something else.
    collate = {
        $copies = foreach ($role in $Roles) { '--edit-copy', $CopyFile[$role] }
        Invoke-Checked -Stage 'collate' -Expect 4 -CommandLine ($Launcher + @(
            $Cmd.collate, '--stage', '4', '--binder', $BinderFile, '--topology', $TopologyFile
        ) + $copies + @(
            '--out', $ChiefFile, '--proof-out', $Proof0File, '--batch-out', $Batch1File
        ))
        # Process #178, beside the main line: the same fixture written to a
        # second tree, gathered, and a copy seeded from that binder. Handed to
        # `collate` alongside the four real copies it is one copy from another
        # tree, whose addresses answer to another address space, and the round
        # rolls back. The copy is unruled, so the report also carries one line
        # per place it left alone; what is asserted is the root line, the exit
        # code, and that nothing was written.
        New-Item -ItemType Directory -Path $OtherDir | Out-Null
        Invoke-Checked -Stage 'other fixture' -CommandLine @(
            'uv', 'run', 'python', '-c',
            $WriteFixtures,
            $OtherDir
        )
        Invoke-Checked -Stage 'other gather' -CommandLine ($Launcher + @(
            $Cmd.gather, '--repo', $OtherDir, '--out', $OtherBinderFile,
            (Join-Path $OtherDir 'fib.py'), (Join-Path $OtherDir 'rate.py'),
            (Join-Path $OtherDir 'store.py')
        ))
        Invoke-Checked -Stage 'other distribute' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--topology', $TopologyFile, '--stage', '4',
            '--binder', $OtherBinderFile, '--out-dir', $OtherCopiesDir
        ))
        $otherCopy = @(Get-ChildItem -LiteralPath $OtherCopiesDir -File | Where-Object {
            (Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json).role -eq 'ownership-context'
        })[0].FullName
        $mismatched = $Launcher + @(
            $Cmd.collate, '--stage', '4', '--binder', $BinderFile
        ) + $copies + @('--edit-copy', $otherCopy) + @(
            '--out', $OtherChiefFile, '--proof-out', $OtherProofFile,
            '--batch-out', $OtherBatchFile
        )
        $refused = Invoke-Checked -Stage 'collate from two trees refused' -Expect 1 -Capture -CommandLine $mismatched
        if (-not (($refused -join "`n").Contains('copies from different trees share no address space'))) {
            Write-Host 'stage failed: collate from two trees refused'
            Write-Host 'expected a refusal naming the two trees; collate printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $mismatched)"
            exit 1
        }
        foreach ($written in @($OtherChiefFile, $OtherProofFile, $OtherBatchFile)) {
            if (Test-Path -LiteralPath $written) {
                Write-Host 'stage failed: collate from two trees refused'
                Write-Host "a rolled-back collate wrote $written"
                exit 1
            }
        }
    }
    # One turn. `write_answers` writes each role's answers to the batch
    # `collate` sent, from `ANSWERS` in smoke_fixture.py. `check --answers`
    # reads each file against that batch alone -- the slot it was sent
    # carries the question its answer is read against -- and exits 1 on a
    # slot left unanswered, which `turn` refuses the whole round for. Then
    # `turn` folds all four roles' answers onto the places the proof carries;
    # it reads neither the binder nor the batch, since the places say who
    # each was put to. The answers leave b8 and c3 holding an add beside
    # another role's answer to it, and a3 and b9 two corrections each, so
    # four places are still carried forward and `turn`, whose exit codes are
    # `collate`'s, exits 4.
    turn = {
        Invoke-Checked -Stage 'plant-answers' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_answers; write_answers(Path(sys.argv[1]))',
            $Run
        )
        # `write_answers` names each role's file after the role; named here
        # to match rather than read back from what it returns.
        $answerFile = @{}
        foreach ($role in $Roles) {
            $answerFile[$role] = Join-Path $Run "answers-$role.json"
            # No --repo: the slots the batch sent name the tree they were read
            # from, so the check resolves an answer's citations against it
            # without being told where the checkout is.
            Invoke-Checked -Stage "check answers $role" -CommandLine ($Launcher + @(
                $Cmd.check, '--answers', $answerFile[$role], '--sent', $Batch1File,
                '--role', $role
            ))
        }
        # Process #181, beside the main line: the same role's answers with one
        # source cited past the end of the page it names. An answer's sources
        # are verified before the fold, as a mark's are, so `check --answers`
        # names it and `turn` refuses the whole round for it and writes
        # nothing.
        $badCite = Invoke-Checked -Stage 'plant-bad-cite' -Capture -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_bad_cite_answers; print(write_bad_cite_answers(Path(sys.argv[1])))',
            $Run
        )
        $badCiteFile = @($badCite)[-1]
        $badCheck = $Launcher + @(
            $Cmd.check, '--answers', $badCiteFile, '--sent', $Batch1File,
            '--role', 'block-context'
        )
        $refused = Invoke-Checked -Stage 'check answers bad cite refused' -Expect 1 -Capture -CommandLine $badCheck
        if (-not (($refused -join "`n").Contains('names a line past the end of the file'))) {
            Write-Host 'stage failed: check answers bad cite refused'
            Write-Host 'expected a refusal naming the cite that does not resolve; check printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $badCheck)"
            exit 1
        }
        $badAnswers = foreach ($role in $Roles) {
            '--answers', ($role -eq 'block-context' ? "$role=$badCiteFile" : "$role=$($answerFile[$role])")
        }
        $badTurn = $Launcher + @($Cmd.turn, '--proof', $Proof0File) + $badAnswers + @(
            '--proof-out', $BadCiteProofFile, '--batch-out', $BadCiteBatchFile
        )
        $refused = Invoke-Checked -Stage 'turn bad cite refused' -Expect 1 -Capture -CommandLine $badTurn
        if (-not (($refused -join "`n").Contains('names a line past the end of the file'))) {
            Write-Host 'stage failed: turn bad cite refused'
            Write-Host 'expected a refusal naming the cite that does not resolve; turn printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $badTurn)"
            exit 1
        }
        foreach ($written in @($BadCiteProofFile, $BadCiteBatchFile)) {
            if (Test-Path -LiteralPath $written) {
                Write-Host 'stage failed: turn bad cite refused'
                Write-Host "a rolled-back turn wrote $written"
                exit 1
            }
        }
        $answers = foreach ($role in $Roles) { '--answers', "$role=$($answerFile[$role])" }
        Invoke-Checked -Stage 'turn' -Expect 4 -CommandLine ($Launcher + @(
            $Cmd.turn, '--proof', $Proof0File
        ) + $answers + @(
            '--proof-out', $Proof1File, '--batch-out', $Batch2File
        ))
    }
    # `disposition` folds the chief's rulings over the places the turn left
    # carried forward into the closed proof. The rulings are
    # dispositions.json, which `write_texts` wrote at the mark stage from
    # `DISPOSITIONS` in smoke_fixture.py.
    disposition = {
        Invoke-Checked -Stage 'disposition' -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $Proof1File,
            '--dispositions', $DispositionsFile, '--out', $ChiefFinalFile,
            '--proof-out', $FinalFile
        ))
    }
    # `proof --to-docket` transcribes the closed chief copy into a docket and
    # stops. `proof --from-docket` then reads that docket as the write end
    # reads one, and pulls it into a revise of the original tree at
    # $ProofDir, which must not exist yet -- so a docket the write end
    # refuses stops the smoke at proof-from-docket.
    proof = {
        Invoke-Checked -Stage 'proof-to-docket' -CommandLine ($Launcher + @(
            $Cmd.proof, '--copy', $ChiefFinalFile, '--repo', $OriginalDir,
            '--to-docket', $DocketFile
        ))
        Invoke-Checked -Stage 'proof-from-docket' -CommandLine ($Launcher + @(
            $Cmd.proof, '--from-docket', $DocketFile, '--repo', $OriginalDir,
            '--out', $ProofDir
        ))
    }
    # The diff is the assertion: `write_expected` writes the text
    # smoke_fixture.py says the plant makes land, and git compares it with
    # the proof, with core.autocrlf off so a line ending that differs is a
    # difference. Exit 0 means the proof is exactly what was planted. On a
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
    # The second stage, which reads what the first one pulled. Its topology row
    # says `reads = "revise:4"`, so `distribute` is handed that revise root and
    # refuses a binder gathered from anywhere else -- the stage's own `reads`
    # deciding the tree rather than a path typed here. The binder is gathered
    # over the revise's fib.py, whose addresses are its own and not the
    # original's, and the one role corrects a paragraph the first stage already
    # corrected, so the correction is measured against the revised text. Every
    # other prose place is cleaned, and the diff is what says the revise still
    # carries the paragraphs nobody changed.
    second = {
        Invoke-Checked -Stage 'second gather' -CommandLine ($Launcher + @(
            $Cmd.gather, '--repo', $ProofDir, '--revise', '1',
            '--out', $SecondBinderFile, (Join-Path $ProofDir 'fib.py')
        ))
        Invoke-Checked -Stage 'second distribute' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--topology', $TopologyFile, '--stage', $SecondStage,
            '--binder', $SecondBinderFile, '--revise', $ProofDir,
            '--out-dir', $SecondCopiesDir
        ))
        $secondCopy = @(Get-ChildItem -LiteralPath $SecondCopiesDir -File)[0].FullName
        # A binder gathered from the original is refused for the same stage,
        # so what the stage reads is what decides the seeding rather than
        # whichever binder the caller reached for.
        $wrongTree = $Launcher + @(
            $Cmd.distribute, '--topology', $TopologyFile, '--stage', $SecondStage,
            '--binder', $BinderFile, '--revise', $ProofDir,
            '--out-dir', (Join-Path $Run 'copies2-refused')
        )
        $refused = Invoke-Checked -Stage 'second distribute from the original refused' -Expect 2 -Capture -AndErrors -CommandLine $wrongTree
        if (-not (($refused -join "`n").Contains('a stage is seeded from the revise it reads'))) {
            Write-Host 'stage failed: second distribute from the original refused'
            Write-Host 'expected a refusal naming the revise the stage reads; distribute printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $wrongTree)"
            exit 1
        }
        Invoke-Checked -Stage 'second plant' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_second_plant; write_second_plant(Path(sys.argv[1]))',
            $Run
        )
        Invoke-Checked -Stage 'second correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $secondCopy, '--address', 'fib.py@a0',
            '--instruction', 'correct',
            '--false', "@$(Join-Path $Run 'second-a0-false.txt')",
            '--true', "@$(Join-Path $Run 'second-a0-true.txt')",
            '--reason', 'what the count is for is the point, not that it happens',
            '--cite', 'fib.py:1', '--repo', $ProofDir
        ))
        $secondClean = Get-Content -LiteralPath (Join-Path $Run 'second-clean.json') -Raw | ConvertFrom-Json
        foreach ($address in $secondClean) {
            Invoke-Checked -Stage "second clean $address" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $secondCopy, '--address', $address,
                '--instruction', 'clean', '--repo', $ProofDir
            ))
        }
        Invoke-Checked -Stage 'second check' -CommandLine ($Launcher + @(
            $Cmd.check, '--edit-copy', $secondCopy, '--binder', $SecondBinderFile
        ))
        # One role read the place, so its proposal stands with nothing to
        # carry forward and no turn to run (Process #180). collate exits 0.
        Invoke-Checked -Stage 'second collate' -CommandLine ($Launcher + @(
            $Cmd.collate, '--stage', $SecondStage, '--binder', $SecondBinderFile,
            '--topology', $TopologyFile, '--repo', $ProofDir,
            '--edit-copy', $secondCopy, '--out', $SecondChiefFile,
            '--proof-out', $SecondProofFile
        ))
        Invoke-Checked -Stage 'second proof-to-docket' -CommandLine ($Launcher + @(
            $Cmd.proof, '--copy', $SecondChiefFile, '--repo', $ProofDir,
            '--to-docket', $SecondDocketFile
        ))
        Invoke-Checked -Stage 'second proof-from-docket' -CommandLine ($Launcher + @(
            $Cmd.proof, '--from-docket', $SecondDocketFile, '--repo', $ProofDir,
            '--out', $SecondProofDir
        ))
        New-Item -ItemType Directory -Path $SecondExpectedDir | Out-Null
        Invoke-Checked -Stage 'second expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_second_expected; write_second_expected(Path(sys.argv[1]))',
            $SecondExpectedDir
        )
        Invoke-Checked -Stage 'second diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $SecondExpectedDir, $SecondProofDir
        ) -OnFailure {
            Write-Host 'what the second stage did -- the revise against its proof:'
            & git -c core.autocrlf=false --no-pager diff --no-index -- $ProofDir $SecondProofDir | Out-Host
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

# Without this an in-process caller's $LASTEXITCODE would hold the last
# native command's code -- collate's expected 4, for a run stopped there.
exit 0
