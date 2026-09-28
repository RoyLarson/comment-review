# Drives the middle stages of the comment-review chain over a fixture tree,
# for a smoke check that the chain from gather through proof still
# composes: a binder, a topology, seeded copies, the planted marks, the
# fold's proof, two turns in which every role answers what the fold carried
# forward, the chief's dispositions closing what the turns still carry
# forward, the docket
# `proof` transcribes from the closed proof, and the
# revise `proof` pulls from that docket. The diff stage compares that revise
# with the text smoke_fixture.py says the plant makes land, and passes
# only when the two are identical. The partial stage runs the same closed
# proof through the author's approval of two of its places and diffs the one
# page that leaves. The last stage runs a second editorial
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
$TallyFile = Join-Path $OriginalDir 'tally.py'
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
# The second turn's own outputs. `proof2.json` belongs to the second editorial
# stage further down, so the proof this turn writes is named for the turn.
$TurnTwoProofFile = Join-Path $Run 'proof-turn2.json'
$Batch3File = Join-Path $Run 'batch3.json'
$DispositionsFile = Join-Path $Run 'dispositions.json'
# The chief's first ruling leaves the ends of the move it split carried: what
# that call writes, and the rulings the second call takes on its proof.
$ChiefPlacedFile = Join-Path $Run 'chief-placed.json'
$PlacedFile = Join-Path $Run 'placed.json'
$EndsFile = Join-Path $Run 'dispositions-ends.json'
$ChiefFinalFile = Join-Path $Run 'chief-final.json'
$FinalFile = Join-Path $Run 'final.json'
$DocketFile = Join-Path $Run 'docket.json'
$ProofDir = Join-Path $Run 'proof'
$ExpectedDir = Join-Path $Run 'expected'
# The partial approval (Process #192): the places the author approved, the
# revise `proof --only` pulls for them, the page that revise must hold, and
# the same two for the approval of one end of an agreed move alone
# (Process #195 item 5).
$ApprovalFile = Join-Path $Run 'approval.json'
$PartialDir = Join-Path $Run 'partial'
$PartialExpectedDir = Join-Path $Run 'partial-expected'
$OneEndDir = Join-Path $Run 'one-end'
$OneEndExpectedDir = Join-Path $Run 'one-end-expected'
# The author's answers to the roles' human questions (Process #197, #198):
# the TOML answers file `collate`, `turn` and `check` read with --human, and
# the places whose query the asking role replaces once it is answered.
$HumanFile = Join-Path $Run 'human.toml'
$HumanReplacedFile = Join-Path $Run 'human-replaced.json'
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

# The ungathered-destination sub-plant (Process #187): a tree holding the
# three fixture files and a fourth the binder never gathered, a copy seeded
# from the smoke's binder and ruled by hand, and the three paths a refused
# collate must not write.
$UngatheredDir = Join-Path $Run 'ungathered'
$UngatheredCopyFile = Join-Path $Run 'ungathered-copy.json'
$UngatheredChiefFile = Join-Path $Run 'ungathered-chief.json'
$UngatheredProofFile = Join-Path $Run 'ungathered-proof.json'
$UngatheredBatchFile = Join-Path $Run 'ungathered-batch.json'

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

# The compacting stage (Process #193): its plant, the binder gathered over the
# first stage's revise, the copy it is dealt, and what its own proof pulls.
# The refusal sub-plant needs no path of its own -- `mark` writes nothing on a
# ruling it refuses.
$CompactingStage = '6'
$CompactingFile = Join-Path $Run 'compacting.json'
$CompactingBinderFile = Join-Path $Run 'binder3.json'
$CompactingCopiesDir = Join-Path $Run 'copies3'
$CompactingChiefFile = Join-Path $Run 'chief3.json'
$CompactingProofFile = Join-Path $Run 'proof3.json'
$CompactingDocketFile = Join-Path $Run 'docket3.json'
$CompactingProofDir = Join-Path $Run 'proof3'
$CompactingExpectedDir = Join-Path $Run 'compacted-expected'
# The widened-copy sub-plant (Process #193): a copy that added `correct` to
# what it says it admits, and the two paths a refused collate must not write.
$WidenedCopyFile = Join-Path $Run 'copy3-widened.json'
$WidenedChiefFile = Join-Path $Run 'chief3-widened.json'
$WidenedProofFile = Join-Path $Run 'proof3-widened.json'

# The one-liner that writes the four fixture files into a directory, used by
# the fixture stage and by the second tree the root refusal sub-plant gathers.
$WriteFixtures = 'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_fixture, write_rate_fixture, write_store_fixture, write_tally_fixture; root = Path(sys.argv[1]); write_fixture(root); write_rate_fixture(root); write_store_fixture(root); write_tally_fixture(root)'

# Stops the script unless every line in -Expected is one of the lines a
# command printed, whole. A command's report names each human question on a
# line of its own, so a line matched whole is the question and its answer as
# the command put them, not a fragment that could sit inside another line.
function Assert-Lines {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [AllowEmptyCollection()] [string[]]$Printed,
        [Parameter(Mandatory)] [string[]]$Expected,
        [Parameter(Mandatory)] [string[]]$CommandLine
    )
    $missing = @($Expected | Where-Object { @($Printed) -notcontains $_ })
    if ($missing.Count -gt 0) {
        Write-Host "stage failed: $Stage"
        Write-Host 'expected the lines:'
        $missing | ForEach-Object { Write-Host "  $_" }
        Write-Host 'the command printed:'
        $Printed | Out-Host
        Write-Host "command: $(Format-CommandLine $CommandLine)"
        exit 1
    }
}

# Stops the script if a command that rolled back wrote any of -Paths.
function Assert-NotWritten {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [string[]]$Paths
    )
    foreach ($written in $Paths) {
        if (Test-Path -LiteralPath $written) {
            Write-Host "stage failed: $Stage"
            Write-Host "a rolled-back command wrote $written"
            exit 1
        }
    }
}

# The lines a command prints for the human questions `write_human` answers
# up to -Stage: `asks the human <at>: <role> -- <question>; <tail>` before
# the answer is recorded, `answered by the human <at>: <role> -- <answer>;
# <tail>` once it is. The tail is the command's own, so each caller names it,
# writing {role} where the command names the role that asked.
function Get-HumanLines {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [ValidateSet('asks', 'answered')] [string]$As,
        [Parameter(Mandatory)] [string]$Tail
    )
    $json = & uv run python -c 'import json, sys; sys.path.insert(0, "scripts"); from smoke_fixture import HUMAN; print(json.dumps(HUMAN[sys.argv[1]]))' $Stage
    foreach ($one in ($json | ConvertFrom-Json)) {
        $end = $Tail.Replace('{role}', $one.role)
        if ($As -eq 'asks') {
            "asks the human $($one.at): $($one.role) -- $($one.question); $end"
        } else {
            "answered by the human $($one.at): $($one.role) -- $($one.answer); $end"
        }
    }
}

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
            $FixtureFile, $RateFile, $StoreFile, $TallyFile
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
        # And a third, appended by hand, because the three keys a compacting
        # stage carries are not what `--build`'s directives spell (Process
        # #193). It reads the FIRST stage's revise, where the pages the plant
        # writes over-cap prose on are; `topology --verify` below reads the
        # whole file, so the appended row is held to the same parse as the
        # built ones.
        Invoke-Checked -Stage 'plant-compacting' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_compacting; write_compacting(Path(sys.argv[1]))',
            $Run
        )
        $row = (Get-Content -LiteralPath $CompactingFile -Raw | ConvertFrom-Json).row
        [System.IO.File]::AppendAllText($TopologyFile, $row)
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
        # The places `summary` adds, which every role cleans below. The
        # compacting stage's plant was written at the topology stage, which
        # needed its row; this reads the one value the mark stage wants.
        $Untouched = (Get-Content -LiteralPath $CompactingFile -Raw | ConvertFrom-Json).untouched
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
            store_b9 = Join-Path $Run 'store-b9.txt'
            store_b10 = Join-Path $Run 'store-b10.txt'
            store_b11 = Join-Path $Run 'store-b11.txt'
            store_b12 = Join-Path $Run 'store-b12.txt'
            store_b7_false = Join-Path $Run 'store-b7-false.txt'
            store_b7_true = Join-Path $Run 'store-b7-true.txt'
            store_c5_false = Join-Path $Run 'store-c5-false.txt'
            store_c5_true = Join-Path $Run 'store-c5-true.txt'
            tally_b1 = Join-Path $Run 'tally-b1.txt'
            tally_b3 = Join-Path $Run 'tally-b3.txt'
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
        # a1 -- the code concern (Process #199), read from code-concern.json,
        # which `write_texts` wrote from `CODE_CONCERN`: a human-review query
        # whose `settles` reads `code concern`. block-context raises it; the
        # other three have nothing to add. `check` names it, and the collate
        # stage has the author answer it `add a TODO` and block-context
        # replace it with a correct and the TODO before the fold.
        $concern = Get-Content -LiteralPath (Join-Path $Run 'code-concern.json') -Raw | ConvertFrom-Json
        Invoke-Checked -Stage "mark $($concern.address) block-context code concern" -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', $concern.address,
            '--instruction', 'query', '--shape', $concern.shape,
            '--attempted', $concern.attempted,
            '--settles', $concern.settles,
            '--reason', $concern.reason,
            '--cite', $concern.cite, '--repo', $OriginalDir
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
        # store.py@b5 -- the contested placement. module-context moves the
        # whole paragraph to store.py@b12, the gap between the last two
        # functions, so its `--change` and its `--raw-text` are one text;
        # block-context reads the same place and marks a human-review query.
        # The collate stage has the author answer it and block-context
        # replace it with a clean, which leaves it owed a say on the
        # placement; it stets the move in both turns, and the chief rules the
        # placement once, for the original, in DISPOSITIONS (Process #201).
        # The other two roles defer.
        Invoke-Checked -Stage 'mark store.py@b5 module-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'store.py@b5',
            '--instruction', 'move', '--from', 'store.py@b5', '--to', 'store.py@b12',
            '--change', "@$($LandingFile.store_b12)", '--raw-text', "@$($LandingFile.store_b12)",
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
        # store.py@b9 -- the agreed move. block-context moves the whole
        # paragraph up to store.py@b8, the gap above the declaration it
        # describes; function-context rewords it where it stands, so it is
        # owed a say on the placement, and both ends are to come until the
        # placement is decided (Process #200, #201). It agrees in the first
        # turn, the move is split into block-context's drop at b9 and add at
        # b8, and the second turn asks each end: the three other roles clean
        # the add, and the drop against the rewording is an escalation the
        # chief rules in DISPOSITIONS (Process #195).
        Invoke-Checked -Stage 'mark store.py@b9 block-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'store.py@b9',
            '--instruction', 'move', '--from', 'store.py@b9', '--to', 'store.py@b8',
            '--change', "@$($LandingFile.store_b9)", '--raw-text', "@$($LandingFile.store_b8)",
            '--reason', 'the paragraph says what total is for, which is read above the declaration',
            '--cite', 'store.py:22', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark store.py@b9 function-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'store.py@b9',
            '--instruction', 'correct',
            '--false', 'number of lookups', '--true', 'count of lookups',
            '--reason', 'the body returns a count, and count is the word the module uses',
            '--cite', 'store.py:23', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'module-context')) {
            Invoke-Checked -Stage "mark store.py@b9 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'store.py@b9',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the comment against the declaration it sits under',
                '--settles', 'block-context',
                '--reason', 'where this note belongs on the page is not my remit',
                '--cite', 'store.py:22', '--repo', $OriginalDir
            ))
        }
        # store.py@b11 -- the move its own filer withdraws. module-context
        # takes the paragraph's second sentence to store.py@b10, the gap above
        # the declaration; block-context rewords that same sentence where it
        # stands, so it is owed a say on the placement -- the two roles that
        # defer at the origin defer on the move -- and both ends are to come
        # while the placement is undecided. block-context stets it in the
        # first turn, so it is put again to both roles; in the second,
        # module-context withdraws it and the move is off at both of its ends
        # (Process #129, #195). The origin's rewording is then a text
        # module-context has not seen, carried past the last turn, and the
        # chief takes it in in DISPOSITIONS.
        Invoke-Checked -Stage 'mark store.py@b11 module-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'store.py@b11',
            '--instruction', 'move', '--from', 'store.py@b11', '--to', 'store.py@b10',
            '--change', "@$($LandingFile.store_b11)", '--raw-text', "@$($LandingFile.store_b10)",
            '--reason', 'the sentence is about the store as a whole, not about this lookup',
            '--cite', 'store.py:28', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark store.py@b11 block-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'store.py@b11',
            '--instruction', 'correct',
            '--false', 'Every lookup', '--true', 'Each lookup',
            '--reason', 'the function is handed one key, so one lookup is what it answers',
            '--cite', 'store.py:28', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context')) {
            Invoke-Checked -Stage "mark store.py@b11 $role query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'store.py@b11',
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'block-context',
                '--reason', 'which of the two sentences belongs here is not my remit',
                '--cite', 'store.py:28', '--repo', $OriginalDir
            ))
        }
        # `summary`'s five places, which this stage leaves alone: length is no
        # concern of the four editorial roles (Process #193), so each of them
        # cleans all five and the paragraphs reach the revise as the fixture
        # wrote them. The compacting stage below is what reads them, and two
        # of the five are what it deals.
        foreach ($address in $Untouched) {
            foreach ($role in $Roles) {
                Invoke-Checked -Stage "mark $address $role clean" -CommandLine ($Launcher + @(
                    $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', $address,
                    '--instruction', 'clean', '--repo', $OriginalDir
                ))
            }
        }
        # tally.py@b1 -- the chief's two-step ruling. module-context takes the
        # paragraph's second sentence to tally.py@b3, the comment in
        # `repeats`, as the partial move at store.py@b1 does, and cleans b3
        # beside its own move. function-context corrects b3 where it stands
        # and cleans b1, and block-context cleans both, so each is owed a say
        # on the placement; ownership-context defers at both. block-context
        # stets the move in both turns, so it is contested when the turns are
        # spent: the chief takes module-context's side, which splits the move
        # and leaves both ends carried, and then rules each end.
        Invoke-Checked -Stage 'mark tally.py@b1 module-context move' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'tally.py@b1',
            '--instruction', 'move', '--from', 'tally.py@b1', '--to', 'tally.py@b3',
            '--change', "@$($LandingFile.tally_b1)", '--raw-text', "@$($LandingFile.tally_b3)",
            '--reason', 'a repeat is what repeats counts, so the sentence defines it there',
            '--cite', 'tally.py:7', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark tally.py@b3 module-context clean' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'tally.py@b3',
            '--instruction', 'clean', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark tally.py@b3 function-context correct' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'tally.py@b3',
            '--instruction', 'correct',
            '--false', 'asked again', '--true', 'asked for a key again',
            '--reason', 'a lookup that repeats asks for a key, not for anything at all',
            '--cite', 'tally.py:8', '--repo', $OriginalDir
        ))
        Invoke-Checked -Stage 'mark tally.py@b1 function-context clean' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'tally.py@b1',
            '--instruction', 'clean', '--repo', $OriginalDir
        ))
        foreach ($address in @('tally.py@b1', 'tally.py@b3')) {
            Invoke-Checked -Stage "mark $address block-context clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', $address,
                '--instruction', 'clean', '--repo', $OriginalDir
            ))
            Invoke-Checked -Stage "mark $address ownership-context query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile['ownership-context'], '--address', $address,
                '--instruction', 'query', '--shape', 'outside-my-role',
                '--attempted', 'read the paragraph against the code at this place',
                '--settles', 'block-context',
                '--reason', 'which function a sentence about repeats belongs to is not my remit',
                '--cite', 'tally.py:2', '--repo', $OriginalDir
            ))
        }
    }
    # `check` over each of the four copies, before `collate`, whose exit code
    # cannot say the same: collate is expected to exit 4 below, and in its
    # exit codes an escalation outranks a place a role left unruled, so a
    # copy short of a ruling would still meet that expectation. `check`
    # exits 1 on it.
    #
    # block-context's copy holds the two human-review queries the mark stage
    # planted, at fib.py@a1 and store.py@b5, and nothing else the fold would
    # send back, so `check` names each question and exits 5 (ASKS_THE_HUMAN)
    # rather than 1: the role's part is done, and the task agent asks the
    # author before `collate` folds (Process #197). The other three exit 0.
    check = {
        foreach ($role in $Roles) {
            $checkCopy = $Launcher + @(
                $Cmd.check, '--edit-copy', $CopyFile[$role], '--binder', $BinderFile
            )
            if ($role -ne 'block-context') {
                Invoke-Checked -Stage "check $role" -CommandLine $checkCopy
                continue
            }
            $printed = Invoke-Checked -Stage "check $role asks the human" -Expect 5 -Capture -CommandLine $checkCopy
            Assert-Lines -Stage "check $role asks the human" -Printed $printed -CommandLine $checkCopy -Expected @(
                Get-HumanLines -Stage 'collate' -As 'asks' -Tail "this is the role's part done -- hand the copy back, and the task agent asks it"
            )
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
        # The same comment run onto the paragraph's last line keeps every
        # word, so the row takes it -- and it rewrites that line, beside the
        # line the role's own correct rewrites. Two rewrites of adjacent lines
        # meet, so two of one role's marks there do not compose, and `mark`
        # refuses at placing time what the fold would refuse at the fold
        # (Process #179).
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
    #
    # Before it folds, the two human questions `check` named are answered
    # (Process #197, #198). `write_human` records the author's answers in the
    # TOML answers file; `collate --human` still rolls the round back while a
    # query stands, exit 5, printing each question with its answer and
    # writing nothing. block-context then replaces each query as
    # human-replaced.json says -- `mark --withdraw`, then the marks it files
    # in its place: for the code concern answered `add a TODO`, a correct of
    # the docstring and the TODO's add in the margin of `global CALLS`
    # (Process #199) -- `check` passes its copy, and `collate` folds.
    collate = {
        $copies = foreach ($role in $Roles) { '--edit-copy', $CopyFile[$role] }
        $collateLine = $Launcher + @(
            $Cmd.collate, '--stage', '4', '--binder', $BinderFile, '--topology', $TopologyFile
        ) + $copies + @(
            '--out', $ChiefFile, '--proof-out', $Proof0File, '--batch-out', $Batch1File,
            '--human', $HumanFile
        )
        Invoke-Checked -Stage 'plant-human' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_human; write_human(Path(sys.argv[1]), "collate")',
            $Run
        )
        $printed = Invoke-Checked -Stage 'collate asks the human' -Expect 5 -Capture -CommandLine $collateLine
        Assert-Lines -Stage 'collate asks the human' -Printed $printed -CommandLine $collateLine -Expected @(
            Get-HumanLines -Stage 'collate' -As 'answered' -Tail '{role} replaces this query with its mark or answer'
        )
        Assert-NotWritten -Stage 'collate asks the human' -Paths @($ChiefFile, $Proof0File, $Batch1File)
        foreach ($one in (Get-Content -LiteralPath $HumanReplacedFile -Raw | ConvertFrom-Json)) {
            Invoke-Checked -Stage "replace $($one.query) $($one.role) query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$one.role], '--address', $one.query,
                '--withdraw'
            ))
            foreach ($placed in $one.marks) {
                Invoke-Checked -Stage "replace $($one.query) $($one.role) at $($placed.address)" -CommandLine ($Launcher + @(
                    $Cmd.mark, '--edit-copy', $CopyFile[$one.role], '--address', $placed.address
                ) + @($placed.args) + @('--repo', $OriginalDir))
            }
        }
        Invoke-Checked -Stage 'check block-context replaced' -CommandLine ($Launcher + @(
            $Cmd.check, '--edit-copy', $CopyFile['block-context'], '--binder', $BinderFile,
            '--human', $HumanFile
        ))
        Invoke-Checked -Stage 'collate' -Expect 4 -CommandLine $collateLine
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
            (Join-Path $OtherDir 'store.py'), (Join-Path $OtherDir 'tally.py')
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
        # Process #187, beside the main line: a move into a file the binder
        # never gathered, whose destination text drops a word of the
        # paragraph already there. `collate --repo` reads a tree holding the
        # three fixture files and that fourth one; the copy is every slot
        # ruled clean but the move. The fold measures the destination against
        # the page's paragraph, so the move's own row refuses it and the round
        # rolls back. What is asserted is that line, the exit code, and that
        # nothing was written.
        New-Item -ItemType Directory -Path $UngatheredDir | Out-Null
        Invoke-Checked -Stage 'ungathered fixture' -CommandLine @(
            'uv', 'run', 'python', '-c',
            $WriteFixtures,
            $UngatheredDir
        )
        Invoke-Checked -Stage 'ungathered seed' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--seed', '--binder', $BinderFile,
            '--role', 'block-context', '--out', $UngatheredCopyFile
        ))
        Invoke-Checked -Stage 'ungathered plant' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_ungathered_plant; write_ungathered_plant(Path(sys.argv[1]), Path(sys.argv[2]))',
            $UngatheredCopyFile, $UngatheredDir
        )
        $refusal = (& uv run python -c 'import sys; sys.path.insert(0, "scripts"); from smoke_fixture import UNGATHERED_REFUSAL; print(UNGATHERED_REFUSAL)')
        $ungathered = $Launcher + @(
            $Cmd.collate, '--stage', '4', '--binder', $BinderFile,
            '--repo', $UngatheredDir, '--edit-copy', $UngatheredCopyFile,
            '--out', $UngatheredChiefFile, '--proof-out', $UngatheredProofFile,
            '--batch-out', $UngatheredBatchFile
        )
        $refused = Invoke-Checked -Stage 'collate a move into an ungathered file refused' -Expect 1 -Capture -CommandLine $ungathered
        if (-not (@($refused) -contains $refusal)) {
            Write-Host 'stage failed: collate a move into an ungathered file refused'
            Write-Host "expected the line: $refusal"
            Write-Host 'collate printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $ungathered)"
            exit 1
        }
        foreach ($written in @($UngatheredChiefFile, $UngatheredProofFile, $UngatheredBatchFile)) {
            if (Test-Path -LiteralPath $written) {
                Write-Host 'stage failed: collate a move into an ungathered file refused'
                Write-Host "a rolled-back collate wrote $written"
                exit 1
            }
        }
    }
    # The first turn. `write_answers` writes each role's answers to the batch
    # `collate` sent, from `ANSWERS` in smoke_fixture.py. `check --answers`
    # reads each file against that batch alone -- the slot it was sent
    # carries the question its answer is read against -- and exits 1 on a
    # slot left unanswered, which `turn` refuses the whole round for. Then
    # `turn` folds all four roles' answers onto the places the proof carries;
    # it reads neither the binder nor the batch, since the places say who
    # each was put to. The answers also settle the placement of each move the
    # fold left open: one agreed and split, two stetted and contested. No
    # slot is sent at an end of those moves, which are to come while their
    # placements are undecided. The answers leave b8 and c3 holding an add
    # beside another role's answer to it, a3, b9 and c1 with texts no role
    # has taken, the split's two ends newly asked of the roles that have not
    # seen them, and the two contested moves, so places are carried forward
    # and `turn`, whose exit codes are `collate`'s, exits 4.
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
            $checkAnswers = $Launcher + @(
                $Cmd.check, '--answers', $answerFile[$role], '--sent', $Batch1File,
                '--role', $role
            )
            if ($role -ne 'block-context') {
                Invoke-Checked -Stage "check answers $role" -CommandLine $checkAnswers
                continue
            }
            # block-context answers fib.py@b15 with a human-review query, which
            # `check` names and exits 5 for, as it did for the copy.
            $printed = Invoke-Checked -Stage "check answers $role asks the human" -Expect 5 -Capture -CommandLine $checkAnswers
            Assert-Lines -Stage "check answers $role asks the human" -Printed $printed -CommandLine $checkAnswers -Expected @(
                Get-HumanLines -Stage 'turn' -As 'asks' -Tail "this is the role's part done -- hand the copy back, and the task agent asks it"
            )
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
        # The human question the turn's answers put, answered before the turn
        # folds (Process #197, #198), as collate's were: the author's answer
        # is added to the answers file, `turn --human` rolls back with exit 5
        # and writes nothing while the query stands, block-context rewrites
        # its answer as `REPLACED_ANSWERS` says, `check` passes the file, and
        # the turn folds.
        $answers = foreach ($role in $Roles) { '--answers', "$role=$($answerFile[$role])" }
        $turnLine = $Launcher + @(
            $Cmd.turn, '--proof', $Proof0File
        ) + $answers + @(
            '--proof-out', $Proof1File, '--batch-out', $Batch2File, '--human', $HumanFile
        )
        Invoke-Checked -Stage 'plant-human-turn' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_human; write_human(Path(sys.argv[1]), "turn")',
            $Run
        )
        $printed = Invoke-Checked -Stage 'turn asks the human' -Expect 5 -Capture -CommandLine $turnLine
        Assert-Lines -Stage 'turn asks the human' -Printed $printed -CommandLine $turnLine -Expected @(
            Get-HumanLines -Stage 'turn' -As 'answered' -Tail '{role} replaces this query with its mark or answer'
        )
        Assert-NotWritten -Stage 'turn asks the human' -Paths @($Proof1File, $Batch2File)
        Invoke-Checked -Stage 'replace-answers' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import replace_answers; replace_answers(Path(sys.argv[1]))',
            $Run
        )
        Invoke-Checked -Stage 'check answers block-context replaced' -CommandLine ($Launcher + @(
            $Cmd.check, '--answers', $answerFile['block-context'], '--sent', $Batch1File,
            '--role', 'block-context', '--human', $HumanFile
        ))
        Invoke-Checked -Stage 'turn' -Expect 4 -CommandLine $turnLine
    }
    # The second turn, over the batch the first one wrote. `write_answers2`
    # writes each role's answers from `ANSWERS2` in smoke_fixture.py, which
    # answers every slot that batch carries by name. It is where the withdrawn
    # move is answered: stetted in the first turn, its placement is put again
    # to its mover, which withdraws it here, so the move comes off both of
    # its ends, and to the role that stetted, which defers with a placement
    # query; the withdrawn move's origin then carries a rewording its mover
    # has not seen. The other contested placement is put again too, and
    # stays contested. The agreed move's ends are asked here: the add at
    # store.py@b8 is cleaned and settles, and the drop at store.py@b9 is held
    # against the rewording. Every other place the batch asks about is one
    # the chief rules below, and the answers keep each of them carried
    # forward, so `turn` exits 4 again.
    turn2 = {
        Invoke-Checked -Stage 'plant-answers2' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_answers2; write_answers2(Path(sys.argv[1]))',
            $Run
        )
        $answerFile = @{}
        foreach ($role in $Roles) {
            $answerFile[$role] = Join-Path $Run "answers2-$role.json"
            Invoke-Checked -Stage "check answers2 $role" -CommandLine ($Launcher + @(
                $Cmd.check, '--answers', $answerFile[$role], '--sent', $Batch2File,
                '--role', $role
            ))
        }
        $answers = foreach ($role in $Roles) { '--answers', "$role=$($answerFile[$role])" }
        Invoke-Checked -Stage 'turn2' -Expect 4 -CommandLine ($Launcher + @(
            $Cmd.turn, '--proof', $Proof1File
        ) + $answers + @(
            '--proof-out', $TurnTwoProofFile, '--batch-out', $Batch3File
        ))
    }
    # `disposition` folds the chief's rulings over the places the second turn
    # left carried forward, and its rulings on the two placements it left
    # undecided, in two calls. The first takes dispositions.json, which
    # `write_texts` wrote at the mark stage from `DISPOSITIONS` in
    # smoke_fixture.py. Its ruling on store.py@b5's placement keeps the
    # paragraph where it is, and both ends settle; its ruling on
    # tally.py@b1's takes the mover's side, which splits the move and leaves
    # both ends carried forward: the drop's remainder at the origin is a
    # text the roles that cleaned it have not seen, and at the destination
    # the split's add composes with function-context's correction into one
    # they have not seen either. So the call commits its proof and exits 3,
    # as `collate` does with a place composed. The second call takes that
    # proof and dispositions-ends.json, `ENDS`, which rules the two ends, and
    # closes the proof with exit 0.
    disposition = {
        Invoke-Checked -Stage 'disposition placements' -Expect 3 -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $TurnTwoProofFile,
            '--dispositions', $DispositionsFile, '--out', $ChiefPlacedFile,
            '--proof-out', $PlacedFile
        ))
        Invoke-Checked -Stage 'disposition ends' -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $PlacedFile,
            '--dispositions', $EndsFile, '--out', $ChiefFinalFile,
            '--proof-out', $FinalFile
        ))
    }
    # `proof --to-docket` transcribes the closed proof's decided places into a
    # docket and stops (ruling #184). `proof --from-docket` then reads that
    # docket as the write end reads one, and pulls it into a revise of the
    # original tree at $ProofDir, which must not exist yet -- so a docket the
    # write end refuses stops the smoke at proof-from-docket. $ChiefFinalFile
    # is still written by the disposition stage above, as the record of what
    # was decided; nothing downstream reads it back.
    proof = {
        Invoke-Checked -Stage 'proof-to-docket' -CommandLine ($Launcher + @(
            $Cmd.proof, '--proof', $FinalFile, '--repo', $OriginalDir,
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
    # The partial approval, beside the main line and over the same closed
    # proof (ruling #192): the author approved two of its decided places, so
    # `proof --only` sets those and nothing else. Its revise holds `store.py`
    # alone -- the only page those two places sit on -- and the diff is
    # against a page written by hand as the fixture with those two places set,
    # so a run that set a third place, or set neither, fails here. A second
    # approval names one end of the agreed move alone, which is set as named.
    partial = {
        Invoke-Checked -Stage 'plant-approval' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_approval; write_approval(Path(sys.argv[1]))',
            $Run
        )
        $approval = Get-Content -LiteralPath $ApprovalFile -Raw | ConvertFrom-Json
        $only = @()
        foreach ($address in $approval.approved) {
            $only += @('--only', $address)
        }
        Invoke-Checked -Stage 'partial approval' -CommandLine ($Launcher + @(
            $Cmd.proof, '--proof', $FinalFile, '--repo', $OriginalDir
        ) + $only + @('--out', $PartialDir))
        New-Item -ItemType Directory -Path $PartialExpectedDir | Out-Null
        Invoke-Checked -Stage 'partial expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_partial_expected; write_partial_expected(Path(sys.argv[1]))',
            $PartialExpectedDir
        )
        Invoke-Checked -Stage 'partial diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $PartialExpectedDir, $PartialDir
        ) -OnFailure {
            Write-Host 'what the partial approval did -- the original against it:'
            & git -c core.autocrlf=false --no-pager diff --no-index -- $OriginalDir $PartialDir | Out-Host
        }
        # One end of the agreed move alone. After the split its two ends are
        # a `drop` and an `add`, approved each on its own (Process #195 item
        # 5), so `proof --only` sets the arrival it names and leaves the
        # departure it does not, and the diff is against the fixture with
        # that one place set.
        Invoke-Checked -Stage 'one end approved' -CommandLine ($Launcher + @(
            $Cmd.proof, '--proof', $FinalFile, '--repo', $OriginalDir,
            '--only', $approval.'one-end', '--out', $OneEndDir
        ))
        New-Item -ItemType Directory -Path $OneEndExpectedDir | Out-Null
        Invoke-Checked -Stage 'one end expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_one_end_expected; write_one_end_expected(Path(sys.argv[1]))',
            $OneEndExpectedDir
        )
        Invoke-Checked -Stage 'one end diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $OneEndExpectedDir, $OneEndDir
        ) -OnFailure {
            Write-Host 'what approving one end did -- the original against it:'
            & git -c core.autocrlf=false --no-pager diff --no-index -- $OriginalDir $OneEndDir | Out-Host
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
            $Cmd.proof, '--proof', $SecondProofFile, '--repo', $ProofDir,
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
    # The compacting stage (Process #193), reading the first stage's revise as
    # its row says. Its binder is gathered over that revise's store.py, whose
    # last function the plant wrote with prose on both sides of the cap; the
    # stage is dealt the two `b` places over it and nothing else, and the copy
    # is what says so. The role condenses one with a `patch` quoting the whole
    # paragraph and leaves the other at length with a `clean` carrying the
    # reason, which is what compact.md asks of a paragraph that cannot come
    # under the cap. A `correct` there is refused by `mark`, naming the stage.
    compacting = {
        $plant = Get-Content -LiteralPath $CompactingFile -Raw | ConvertFrom-Json
        Invoke-Checked -Stage 'compacting gather' -CommandLine ($Launcher + @(
            $Cmd.gather, '--repo', $ProofDir, '--revise', '1',
            '--out', $CompactingBinderFile, (Join-Path $ProofDir 'store.py')
        ))
        Invoke-Checked -Stage 'compacting distribute' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--topology', $TopologyFile, '--stage', $CompactingStage,
            '--binder', $CompactingBinderFile, '--revise', $ProofDir,
            '--out-dir', $CompactingCopiesDir
        ))
        $copy = @(Get-ChildItem -LiteralPath $CompactingCopiesDir -File)[0].FullName
        $held = Get-Content -LiteralPath $copy -Raw | ConvertFrom-Json
        # The deal is the assertion: the copy holds a slot at each place over
        # the cap and at no other, so a stage dealt everything, or nothing,
        # fails here rather than at the diff.
        $slots = @($held.sheets | ForEach-Object { $_.marks } | ForEach-Object { $_.address })
        if (($slots -join ',') -ne ($plant.dealt -join ',')) {
            Write-Host 'stage failed: compacting distribute'
            Write-Host "expected slots at $($plant.dealt -join ', '); the copy holds: $($slots -join ', ')"
            Write-Host "copy: $copy"
            exit 1
        }
        if ($held.stage -ne $CompactingStage) {
            Write-Host 'stage failed: compacting distribute'
            Write-Host "the copy names stage '$($held.stage)', not '$CompactingStage'"
            exit 1
        }
        # The widened copy, taken before the two rulings below: a role that
        # adds `correct` to its own copy's `admits` gets it past `mark`,
        # which reads that field, so `collate` is what holds the marks to the
        # stage's row. Placed on its own copy, so the one the stage returns
        # is untouched.
        Invoke-Checked -Stage 'plant-widened' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import widen; widen(Path(sys.argv[1]), Path(sys.argv[2]))',
            $copy, $WidenedCopyFile
        )
        Invoke-Checked -Stage 'widened correct placed' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $WidenedCopyFile, '--address', $plant.patched,
            '--instruction', $plant.refused,
            '--false', 'Nothing is ever', '--true', 'Nothing is',
            '--reason', 'the sentence reads shorter', '--cite', 'store.py:40',
            '--repo', $ProofDir
        ))
        Invoke-Checked -Stage 'widened clean placed' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $WidenedCopyFile, '--address', $plant.kept,
            '--instruction', 'clean', '--reason', $plant.reason, '--repo', $ProofDir
        ))
        $widened = $Launcher + @(
            $Cmd.collate, '--stage', $CompactingStage, '--binder', $CompactingBinderFile,
            '--topology', $TopologyFile, '--repo', $ProofDir,
            '--edit-copy', $WidenedCopyFile, '--out', $WidenedChiefFile,
            '--proof-out', $WidenedProofFile
        )
        $refused = Invoke-Checked -Stage 'collate over a widened copy refused' -Expect 1 -Capture -CommandLine $widened
        if (-not (($refused -join "`n").Contains("stage $CompactingStage admits"))) {
            Write-Host 'stage failed: collate over a widened copy refused'
            Write-Host 'expected a refusal naming the stage and what it admits; collate printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $widened)"
            exit 1
        }
        foreach ($written in @($WidenedChiefFile, $WidenedProofFile)) {
            if (Test-Path -LiteralPath $written) {
                Write-Host 'stage failed: collate over a widened copy refused'
                Write-Host "a refused collate wrote $written"
                exit 1
            }
        }
        Invoke-Checked -Stage 'compacting patch' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $copy, '--address', $plant.patched,
            '--instruction', 'patch',
            '--from', "@$(Join-Path $Run 'compacting-from.txt')",
            '--to', "@$(Join-Path $Run 'compacting-to.txt')",
            '--reason', 'three lines state what two state, and the cap is two',
            '--repo', $ProofDir
        ))
        Invoke-Checked -Stage 'compacting clean' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $copy, '--address', $plant.kept,
            '--instruction', 'clean', '--reason', $plant.reason, '--repo', $ProofDir
        ))
        # The instruction the row does not admit. `mark` refuses it as it
        # places, so the copy is left exactly as the two rulings above left
        # it -- which the check below is what proves.
        $notAdmitted = $Launcher + @(
            $Cmd.mark, '--edit-copy', $copy, '--address', $plant.patched,
            '--instruction', $plant.refused,
            '--false', 'Nothing is ever', '--true', 'Nothing is',
            '--reason', 'the sentence reads shorter', '--cite', 'store.py:40',
            '--repo', $ProofDir
        )
        $refused = Invoke-Checked -Stage 'compacting correct refused' -Expect 1 -Capture -CommandLine $notAdmitted
        if (-not (($refused -join "`n").Contains("stage $CompactingStage admits"))) {
            Write-Host 'stage failed: compacting correct refused'
            Write-Host 'expected a refusal naming the stage and what it admits; mark printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $notAdmitted)"
            exit 1
        }
        Invoke-Checked -Stage 'compacting check' -CommandLine ($Launcher + @(
            $Cmd.check, '--edit-copy', $copy, '--binder', $CompactingBinderFile,
            '--repo', $ProofDir
        ))
        # One role read each place, so each proposal stands with nothing to
        # carry forward and no turn to run (Process #180). collate exits 0.
        Invoke-Checked -Stage 'compacting collate' -CommandLine ($Launcher + @(
            $Cmd.collate, '--stage', $CompactingStage, '--binder', $CompactingBinderFile,
            '--topology', $TopologyFile, '--repo', $ProofDir,
            '--edit-copy', $copy, '--out', $CompactingChiefFile,
            '--proof-out', $CompactingProofFile
        ))
        Invoke-Checked -Stage 'compacting proof-to-docket' -CommandLine ($Launcher + @(
            $Cmd.proof, '--proof', $CompactingProofFile, '--repo', $ProofDir,
            '--to-docket', $CompactingDocketFile
        ))
        Invoke-Checked -Stage 'compacting proof-from-docket' -CommandLine ($Launcher + @(
            $Cmd.proof, '--from-docket', $CompactingDocketFile, '--repo', $ProofDir,
            '--out', $CompactingProofDir
        ))
        New-Item -ItemType Directory -Path $CompactingExpectedDir | Out-Null
        Invoke-Checked -Stage 'compacting expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_compacted_expected; write_compacted_expected(Path(sys.argv[1]))',
            $CompactingExpectedDir
        )
        Invoke-Checked -Stage 'compacting diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $CompactingExpectedDir, $CompactingProofDir
        ) -OnFailure {
            Write-Host 'what the compacting stage did -- the revise against its proof:'
            & git -c core.autocrlf=false --no-pager diff --no-index -- $ProofDir $CompactingProofDir | Out-Host
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
