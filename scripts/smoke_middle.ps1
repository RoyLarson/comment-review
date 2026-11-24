# Drives the middle stages of the comment-review chain over a fixture tree,
# for a smoke check that the chain from gather through proof still
# composes: a binder, a topology written into the run's jacket, the copies
# `stage open` seeds, the planted marks, the fold's proof, two turns in which
# every role answers what the fold carried forward, and the chief's
# dispositions closing what the turns still carry forward. Each stage closes
# on its closed proof, and the next stage's tree is that proof set over the
# one before it. The diff stage compares the tree stage 5 opens on with the
# text smoke_fixture.py says the plant makes land, and passes only when the
# two are identical. A second and a compacting editorial stage run over the
# trees the jacket builds for them, `proof --jacket` sets the whole run, and
# the partial stage sets the author's approval of two of the first stage's
# places and diffs the one page that leaves.
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
    disposition = 'disposition'; proof = 'proof'; addresses = 'addresses'
    stage = 'stage'
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
# $Run is the jacket's run directory: `stage open` writes each stage's binder,
# root and copies beside the jacket, and records them in it.
$JacketFile = Join-Path $Run 'jacket.json'
$CopiesDir = Join-Path $Run 'copies'

# The four roles stage 4 dispatches to. The open stage fills $CopyFile with
# the copy `stage open` wrote for each, and $ReceivedFile with its received
# binder, which is the binder `check` reads the copy against.
$Roles = @('ownership-context', 'block-context', 'function-context', 'module-context')
$CopyFile = @{}
$ReceivedFile = @{}

$Proof0File = Join-Path $Run 'proof0.json'
$Batch1File = Join-Path $Run 'batch1.json'
$Proof1File = Join-Path $Run 'proof1.json'
$Batch2File = Join-Path $Run 'batch2.json'
# The second turn's own outputs. `proof2.json` belongs to the second editorial
# stage further down, so the proof this turn writes is named for the turn.
$TurnTwoProofFile = Join-Path $Run 'proof-turn2.json'
$Batch3File = Join-Path $Run 'batch3.json'
$DispositionsFile = Join-Path $Run 'dispositions.json'
# The chief's first ruling leaves the ends of the move it agreed carried: what
# that call writes, and the rulings the second call takes on its proof.
$PlacedFile = Join-Path $Run 'placed.json'
$EndsFile = Join-Path $Run 'dispositions-ends.json'
$FinalFile = Join-Path $Run 'final.json'
# What `proof --jacket` sets for the whole run, and the pages it must hold:
# the first stage's expected pages with the second stage's fib.py and the
# compacting stage's store.py written over them.
$ProofDir = Join-Path $Run 'proof'
$ProofExpectedDir = Join-Path $Run 'proof-expected'
$ExpectedDir = Join-Path $Run 'expected'
# The partial approval (Process #192): the places the author approved, the
# revise `proof --only` pulls for them, the page that revise must hold, and
# the same two for the approval of one end of an agreed move alone
# (Process #195 item 5).
$ApprovalFile = Join-Path $Run 'approval.json'
$PartialDir = Join-Path $Run 'partial'
$PartialExpectedDir = Join-Path $Run 'partial-expected'
$OneEndDir = Join-Path $Run 'one-end'
# The author's answers to the roles' human questions (Process #197, #198):
# the TOML answers file `collate`, `turn` and `check` read with --human, and
# the places whose query the asking role replaces once it is answered.
$HumanFile = Join-Path $Run 'human.toml'
$HumanReplacedFile = Join-Path $Run 'human-replaced.json'
$RoleDraftDir = Join-Path $Run 'role-draft'
$RoleExpectedDir = Join-Path $Run 'role-expected'
$CollideCopyFile = Join-Path $Run 'collide-copy.json'
$ParityCopyFile = Join-Path $Run 'parity-copy.json'
$WrapCopyFile = Join-Path $Run 'wrap-copy.json'
$WrapDraftDir = Join-Path $Run 'wrap-draft'
$WrapExpectedDir = Join-Path $Run 'wrap-expected'
$CollideDraftDir = Join-Path $Run 'collide-draft'
$CollideExpectedDir = Join-Path $Run 'collide-expected'
$SameSentenceCopyFile = Join-Path $Run 'same-sentence-copy.json'
$SameSentenceDraftDir = Join-Path $Run 'same-sentence-draft'
$SameSentenceExpectedDir = Join-Path $Run 'same-sentence-expected'

# The root refusal sub-plant (Process #178): a second tree holding the same
# fixture, a binder over it, the copy `distribute --seed` seeds from that
# binder, and where ownership-context's own copy is kept while that one stands
# in its place. The two paths below them are what a refused collate must not
# write.
$OtherDir = Join-Path $Run 'other'
$OtherBinderFile = Join-Path $Run 'other-binder.json'
$OtherCopyFile = Join-Path $Run 'other-copy.json'
$KeptCopyFile = Join-Path $Run 'kept-copy.json'
$OtherProofFile = Join-Path $Run 'other-proof.json'
$OtherBatchFile = Join-Path $Run 'other-batch.json'

# The ungathered-destination sub-plant (Process #187): a checkout holding the
# four fixture files and a fifth the binder never gathered, a run of its own
# whose one stage dispatches block-context alone, and the two paths a refused
# collate must not write.
$UngatheredDir = Join-Path $Run 'ungathered'
$UngatheredBinderFile = Join-Path $Run 'ungathered-binder.json'
$UngatheredRun = Join-Path $Run 'ungathered-run'
$UngatheredJacketFile = Join-Path $UngatheredRun 'jacket.json'
$UngatheredProofFile = Join-Path $Run 'ungathered-proof.json'
$UngatheredBatchFile = Join-Path $Run 'ungathered-batch.json'

# The cite refusal sub-plant (Process #181), and what a refused turn must not
# write.
$BadCiteProofFile = Join-Path $Run 'bad-cite-proof.json'
$BadCiteBatchFile = Join-Path $Run 'bad-cite-batch.json'

# The second stage, whose topology row reads the revise the first stage's
# closed proof makes. `stage open` builds that tree and gathers its binder, so
# the addresses it rules on are the revise's own; the second stage's closed
# proof is what the expected page is compared with, in the tree the next
# stage opens on.
$SecondStage = '5'
$SecondRole = 'ownership-context'
$SecondProofFile = Join-Path $Run 'proof2.json'
# What collate writes for it before the chief rules, and the batch it must not
# write, since no role is owed a turn.
$SecondCollatedFile = Join-Path $Run 'proof2-collated.json'
$SecondBatchFile = Join-Path $Run 'batch-second.json'
$SecondExpectedDir = Join-Path $Run 'second-expected'

# The compacting stage (Process #193): its plant, its proof, and the page
# that proof must make. The refusal sub-plant needs no path of its own --
# `mark` writes nothing on a ruling it refuses.
$CompactingStage = '6'
$CompactingFile = Join-Path $Run 'compacting.json'
$CompactingProofFile = Join-Path $Run 'proof3.json'
$CompactingCollatedFile = Join-Path $Run 'proof3-collated.json'
$CompactingExpectedDir = Join-Path $Run 'compacted-expected'
# The widened-copy sub-plant (Process #193): a copy that added `correct` to
# what it says it admits, where the stage's own copy is kept while it stands
# in its place, and the proof path a refused collate must not write.
$WidenedCopyFile = Join-Path $Run 'copy3-widened.json'
$KeptCompactingCopyFile = Join-Path $Run 'copy3-kept.json'
$WidenedProofFile = Join-Path $Run 'proof3-widened.json'

# The one-liner that writes the four fixture files into a directory, used by
# the fixture stage and by the second tree the root refusal sub-plant gathers.
$WriteFixtures = 'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_fixture, write_rate_fixture, write_store_fixture, write_tally_fixture; root = Path(sys.argv[1]); write_fixture(root); write_rate_fixture(root); write_store_fixture(root); write_tally_fixture(root)'

# Commits a directory's files as a checkout of its own, since a jacket
# records the run's pre-edit commit. core.autocrlf is off so every tree built
# from that commit holds the LF bytes the fixture wrote.
function Initialize-Checkout {
    param(
        [Parameter(Mandatory)] [string]$Stage,
        [Parameter(Mandatory)] [string]$Dir
    )
    Invoke-Checked -Stage "$Stage init" -CommandLine @('git', '-C', $Dir, 'init', '-q')
    Invoke-Checked -Stage "$Stage config" -CommandLine @('git', '-C', $Dir, 'config', 'core.autocrlf', 'false')
    Invoke-Checked -Stage "$Stage add" -CommandLine @('git', '-C', $Dir, 'add', '.')
    Invoke-Checked -Stage "$Stage commit" -CommandLine @(
        'git', '-C', $Dir, '-c', 'user.name=smoke', '-c', 'user.email=smoke@example.invalid',
        'commit', '-q', '-m', 'fixture'
    )
}

# One opened stage as -Jacket records it, each path resolved against the
# jacket's own directory: Root, Binder, and Copies, the copies it dispatched
# in dispatch order, with Received, each copy's received binder, beside them.
function Get-StageEntry {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [string]$Jacket = $JacketFile
    )
    $base = Split-Path -Parent $Jacket
    $entry = (Get-Content -LiteralPath $Jacket -Raw | ConvertFrom-Json).stages.$Name
    $copies = @($entry.dispatched | ForEach-Object { [System.IO.Path]::GetFullPath($_, $base) })
    [pscustomobject]@{
        Root = [System.IO.Path]::GetFullPath($entry.root, $base)
        Binder = [System.IO.Path]::GetFullPath($entry.binder, $base)
        Copies = $copies
        Received = @($copies | ForEach-Object { Join-Path (Join-Path (Split-Path -Parent $_) 'binders') (Split-Path -Leaf $_) })
    }
}

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
# at partial. Each block runs in its own scope, so a variable a stage assigns
# is gone when the next stage starts: what a later stage reads is a path
# above, the jacket, or a table above that a stage fills in place, as open
# fills $CopyFile. Add an entry to $Stages to extend the chain, and a path
# variable above for anything the new stage writes.
$Stages = [ordered]@{
    fixture = {
        New-Item -ItemType Directory -Path $OriginalDir | Out-Null
        Invoke-Checked -Stage 'fixture' -CommandLine @(
            'uv', 'run', 'python', '-c',
            $WriteFixtures,
            $OriginalDir
        )
        Initialize-Checkout -Stage 'fixture' -Dir $OriginalDir
    }
    gather = {
        Invoke-Checked -Stage 'gather' -CommandLine ($Launcher + @(
            $Cmd.gather, '--repo', $OriginalDir, '--out', $BinderFile,
            $FixtureFile, $RateFile, $StoreFile, $TallyFile
        ))
    }
    topology = {
        # Three stages, written into the run's jacket with the pre-edit commit
        # and the scope: the four roles at once, then one role reading the
        # revise the first stage's closed proof makes, then the compacting
        # stage. A jacket's stages are one chain, so `compose` writes each
        # later stage's `reads` as the revise of the stage before it, which is
        # what decides the tree `stage open` builds for it. The compacting
        # stage's cap, series and admits are read off the row the plant
        # writes (Process #193); `--build` verifies the rows it writes, so they
        # are held to the same parse as the built ones.
        Invoke-Checked -Stage 'plant-compacting' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_compacting; write_compacting(Path(sys.argv[1]))',
            $Run
        )
        $compacting = @(Invoke-Checked -Stage 'compacting row' -Capture -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import json, sys, tomllib; row = tomllib.loads(json.load(open(sys.argv[1]))["row"])["stage"][0]; n = row["name"]; print("\n".join(["--stage", n + "=" + row["dispatch"][0]["role"], "--cap", n + "=" + str(row["cap"]), "--series", n + "=" + ",".join(row["series"]), "--admits", n + "=" + ",".join(row["admits"])]))',
            $CompactingFile
        ))
        Invoke-Checked -Stage 'topology-build' -CommandLine ($Launcher + @(
            $Cmd.topology, '--build', '--binder', $BinderFile, '--run', $Run,
            '--ref', 'HEAD', '--repo', $OriginalDir,
            'fib.py', 'rate.py', 'store.py', 'tally.py',
            '--stage', ('4=' + ($Roles -join ',')),
            '--stage', ($SecondStage + '=' + $SecondRole)
        ) + $compacting)
    }
    open = {
        Invoke-Checked -Stage 'stage open 4' -CommandLine ($Launcher + @(
            $Cmd.stage, 'open', '--jacket', $JacketFile, '--stage', '4', '--repo', $OriginalDir
        ))
        # Each copy names its own role, so the copies are found by what they
        # hold rather than by the file names `stage open` gives them. The plant
        # marks one copy per role, so a role with none, or with more than one
        # -- a role stage 4 sharded -- stops the run here.
        $entry = Get-StageEntry -Name '4'
        $written = @(for ($i = 0; $i -lt $entry.Copies.Count; $i++) {
            [pscustomobject]@{
                Role = (Get-Content -LiteralPath $entry.Copies[$i] -Raw | ConvertFrom-Json).role
                Path = $entry.Copies[$i]
                Received = $entry.Received[$i]
            }
        })
        foreach ($role in $Roles) {
            $held = @($written | Where-Object Role -EQ $role)
            if ($held.Count -ne 1) {
                Write-Host 'stage failed: stage open 4'
                Write-Host "copies for ${role}: $($held.Count), where the plant marks one"
                Write-Host "jacket: $JacketFile"
                exit 1
            }
            $CopyFile[$role] = $held[0].Path
            $ReceivedFile[$role] = $held[0].Received
        }
    }
    # One `mark` call per ruling per role: `mark` takes one ruling per call
    # and has no bulk pass. `LANDINGS` in smoke_fixture.py names what each
    # planted place makes land. An empty place is in no copy, since a copy
    # is seeded with the places that hold prose, so an add there creates its
    # slot in its own role's copy and no other role has one to rule on:
    # fib.py's a2, b8, b17 and c3 and the addresses row's place take one call
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
        # `smoke_fixture.file_for` spells. The addresses row's file is not
        # here: it is named at that row from the address `addresses find` returns.
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
            '--anchor', '`__doc__`',
            '--change', 'and why it is counted',
            '--raw-text', "@$($LandingFile.fib_a0)",
            '--reason', 'the module docstring says what it counts but not what for',
            '--cite', 'fib.py:1', '--repo', $OriginalDir
        ))
        foreach ($role in @('ownership-context', 'function-context', 'module-context')) {
            Invoke-Checked -Stage "mark a0 $role clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$role], '--address', 'fib.py@a0',
                '--instruction', 'clean', '--cite', 'fib.py:1', '--repo', $OriginalDir
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
            '--anchor', '`n < 2`',
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
                '--instruction', 'clean', '--cite', 'fib.py:1', '--repo', $OriginalDir
            ))
        }
        # b8 -- the empty gap above `return wrapper`, absent b.
        Invoke-Checked -Stage 'mark b8 block-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', 'fib.py@b8',
            '--instruction', 'add',
            '--missing', 'nothing notes that counting is finished before wrapper returns',
            '--anchor', '`return wrapper`',
            '--change', "@$($LandingFile.fib_b8)",
            '--reason', 'the return is the last step and nothing says so',
            '--cite', 'fib.py:18', '--repo', $OriginalDir
        ))
        # b17 -- the empty closing gap after the dunder-main block, absent b.
        Invoke-Checked -Stage 'mark b17 module-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'fib.py@b17',
            '--instruction', 'add',
            '--missing', 'nothing notes that the module has nothing left to do here',
            '--anchor', '`__main__`',
            '--change', "@$($LandingFile.fib_b17)",
            '--reason', 'the module ends here and nothing says so',
            '--cite', 'fib.py:34', '--repo', $OriginalDir
        ))
        # c3 -- the empty room beside `@functools.wraps(fn)`, absent c.
        Invoke-Checked -Stage 'mark c3 function-context add' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['function-context'], '--address', 'fib.py@c3',
            '--instruction', 'add',
            '--missing', "nothing notes that wraps preserves fn's identity",
            '--anchor', '`functools.wraps`',
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
                '--instruction', 'clean', '--cite', 'fib.py:1', '--repo', $OriginalDir
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
                '--instruction', 'clean', '--cite', 'fib.py:1', '--repo', $OriginalDir
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
            '--instruction', 'clean', '--cite', 'fib.py:1', '--repo', $OriginalDir
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
            '--withdraw', '--instruction', 'correct'
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
                '--instruction', 'clean', '--cite', 'fib.py:1', '--repo', $OriginalDir
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
            '--change', "@$($LandingFile.fib_a2)",
            '--reason', 'wrapper is the declared function; logged only wraps it',
            '--cite', 'fib.py:13', '--repo', $OriginalDir
        ))
        # The addresses row -- one add whose address this script does not
        # spell. It asks `addresses find` for the `b` place at the line
        # `write_texts` put in addresser-row.json, and stops unless the
        # address that comes back is the one beside it there. `addresses`
        # reads the page from the repo and prints one tab-separated line: the
        # address and the line of code as Python's repr quotes it.
        $row = Get-Content -LiteralPath (Join-Path $Run 'addresser-row.json') -Raw | ConvertFrom-Json
        $addresserCommand = $Launcher + @(
            $Cmd.addresses, 'find', '--repo', $OriginalDir, '--file', 'fib.py',
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
        # `write_texts` names an add's file after its address's page and cue,
        # which `smoke_fixture.file_for` spells and this composes to match.
        $addedParts = $addedAddress.Split('@')
        $addedFile = Join-Path $Run ([System.IO.Path]::GetFileNameWithoutExtension($addedParts[0]) + '-' + $addedParts[1] + '.txt')
        Invoke-Checked -Stage "mark $addedAddress module-context add" -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', $addedAddress,
            '--instruction', 'add',
            '--missing', 'nothing says what running the module directly does',
            '--anchor', '`__name__`',
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
                '--instruction', 'clean', '--cite', 'rate.py:1', '--repo', $OriginalDir
            ))
        }
        # rate.py@c3 -- the patch. module-context rewords the trailing
        # comment, citing the page as every patch does.
        # function-context cannot tell whether the wording wants changing and
        # defers with an unable-to-determine query; ownership-context and
        # block-context defer with a scope-declaring query. A query of either
        # shape abstains, so the fold settles the patch alone.
        Invoke-Checked -Stage 'mark rate.py@c3 module-context patch' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $CopyFile['module-context'], '--address', 'rate.py@c3',
            '--instruction', 'patch',
            '--cite', 'rate.py:1',
            '--from', "@$($LandingFile.rate_c3_from)", '--to', "@$($LandingFile.rate_c3_to)",
            '--reason', 'fraction names the ratio the division returns',
            '--repo', $OriginalDir
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
            '--instruction', 'clean', '--cite', 'store.py:1', '--repo', $OriginalDir
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
                '--instruction', 'clean', '--cite', 'store.py:1', '--repo', $OriginalDir
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
        # turn, the move is agreed and stays filed at b9 and b8, and the second
        # turn asks each end: the three other roles clean the arrival at b8,
        # and the empty remainder at b9 against the rewording is an escalation
        # the chief rules in DISPOSITIONS (Process #205).
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
                    '--instruction', 'clean', '--cite', "$(($address -split '@')[0]):1", '--repo', $OriginalDir
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
        # spent: the chief takes module-context's side, which agrees the move
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
            '--instruction', 'clean', '--cite', 'tally.py:1', '--repo', $OriginalDir
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
            '--instruction', 'clean', '--cite', 'tally.py:1', '--repo', $OriginalDir
        ))
        foreach ($address in @('tally.py@b1', 'tally.py@b3')) {
            Invoke-Checked -Stage "mark $address block-context clean" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile['block-context'], '--address', $address,
                '--instruction', 'clean', '--cite', "$(($address -split '@')[0]):1", '--repo', $OriginalDir
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
                $Cmd.check, '--edit-copy', $CopyFile[$role], '--binder', $ReceivedFile[$role]
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
        # copy moves fib.py@b14 to fib.py@b99, a place fib.py does not carry.
        # `mark` runs the same admission and refuses it as it places, so the
        # move is written into the copy by hand, as a role writes its copy
        # with its file-write tool, and check names it.
        Copy-Item -LiteralPath $CopyFile['module-context'] -Destination $ParityCopyFile
        $parityMark = $Launcher + @(
            $Cmd.mark, '--edit-copy', $ParityCopyFile, '--address', 'fib.py@b14',
            '--instruction', 'move', '--from', 'fib.py@b14', '--to', 'fib.py@b99',
            '--change', '    # Two calls per level, which is what the counter measures.',
            '--raw-text', '    # Two calls per level, which is what the counter measures.',
            '--reason', 'the counting note belongs with the counter',
            '--cite', 'fib.py:29', '--repo', $OriginalDir
        )
        $named = Invoke-Checked -Stage 'check parity mark refused' -Expect 1 -Capture -CommandLine $parityMark
        if (-not (($named -join "`n").Contains("carries no place 'b99'"))) {
            Write-Host 'stage failed: check parity mark refused'
            Write-Host 'expected mark to name fib.py@b99 as a place fib.py does not carry; mark printed:'
            $named | Out-Host
            Write-Host "command: $(Format-CommandLine $parityMark)"
            exit 1
        }
        Invoke-Checked -Stage 'check parity plant' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import json, sys; from pathlib import Path; copy = Path(sys.argv[1]); held = json.loads(copy.read_text(encoding="utf-8")); line = Path(sys.argv[2], "fib.py").read_text(encoding="utf-8").splitlines()[28].strip(); text = "    # Two calls per level, which is what the counter measures."; [slot.update({"instruction": "move", "claim": {"from": "fib.py@b14", "to": "fib.py@b99"}, "change": text, "raw_text": text, "reason": "the counting note belongs with the counter", "sources": [{"cite": "fib.py:29", "verbatim": line}]}) for sheet in held["sheets"] for slot in sheet["marks"] if slot["address"] == "fib.py@b14"]; copy.write_text(json.dumps(held, indent=2), encoding="utf-8")',
            $ParityCopyFile, $OriginalDir
        )
        $parity = $Launcher + @($Cmd.check, '--edit-copy', $ParityCopyFile, '--binder', $ReceivedFile['module-context'])
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
        # copy so the fold still reads the role's own. Each refusal below
        # writes nothing, and the composing same-sentence move is placed on a
        # copy of its own -- so the collide copy the draft reads holds the one
        # move placed on it.
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
        # A second correct from the same role rewriting the word its own
        # correct already rewrites: the two edit the same words, so they do
        # not compose, and `mark` refuses at placing time what the fold would
        # refuse at the fold (Process #390, #397). A move cannot be the second
        # mark here -- its destination keeps every word of the paragraph, so
        # it only inserts, and the correct rewrites one word.
        $sameWords = $Launcher + @(
            $Cmd.mark, '--edit-copy', $CollideCopyFile, '--address', 'rate.py@b1',
            '--instruction', 'correct',
            '--false', 'never above one', '--true', 'never past one',
            '--reason', 'past names the bound the division never crosses',
            '--cite', 'rate.py:7', '--repo', $OriginalDir
        )
        $refused = Invoke-Checked -Stage 'draft collide same words refused' -Expect 1 -Capture -AndErrors -CommandLine $sameWords
        if (-not (($refused -join "`n").Contains('edit the same words and do not compose'))) {
            Write-Host 'stage failed: draft collide same words refused'
            Write-Host 'expected a refusal naming the two marks that do not compose; mark printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $sameWords)"
            exit 1
        }
        # The moved comment run onto the paragraph's last line keeps every
        # word, so the row takes it, and it edits other words of the sentence
        # the correct rewrites -- so the two compose (Process #390). It is
        # placed on a copy of its own, so the collide copy keeps one move, and
        # `write_same_sentence_draft` writes what its draft makes of each page.
        Copy-Item -LiteralPath $CollideCopyFile -Destination $SameSentenceCopyFile
        Invoke-Checked -Stage 'draft collide same sentence mark' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $SameSentenceCopyFile, '--address', 'rate.py@b5',
            '--instruction', 'move', '--from', 'rate.py@b5', '--to', 'rate.py@b1',
            '--change', '    # Kept for callers that ask for a share rather than a rate.',
            '--reason', "share's comment says what rate's does, and belongs with it",
            '--cite', 'rate.py:11', '--repo', $OriginalDir,
            '--raw-text', "@$(Join-Path $Run 'collide-same-sentence.txt')"
        ))
        Invoke-Checked -Stage 'draft collide same sentence' -CommandLine ($Launcher + @(
            $Cmd.proof, '--copy', $SameSentenceCopyFile, '--repo', $OriginalDir,
            '--out', $SameSentenceDraftDir
        ))
        New-Item -ItemType Directory -Path $SameSentenceExpectedDir | Out-Null
        Invoke-Checked -Stage 'draft collide same sentence expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_same_sentence_draft; write_same_sentence_draft(Path(sys.argv[1]))',
            $SameSentenceExpectedDir
        )
        Invoke-Checked -Stage 'draft collide same sentence diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $SameSentenceExpectedDir, $SameSentenceDraftDir
        )
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
        # either side onto one line. A copy seeded again holds no rulings, so
        # ownership-context's fresh copy, seeded from the binder it received,
        # carries this one drop alone, and its draft of rate.py is compared
        # with smoke_fixture.py's WRAP_RATE_DRAFT: the paragraph rewrapped to
        # b1's widest before it.
        Invoke-Checked -Stage 'wrap seed' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--seed', '--binder', $ReceivedFile['ownership-context'],
            '--role', 'ownership-context', '--out', $WrapCopyFile
        ))
        $wrapCopy = $WrapCopyFile
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
        # The jacket names the stage's row, binder and copies, so collate is
        # handed the stage and nothing it folds.
        $collateLine = $Launcher + @(
            $Cmd.collate, '--jacket', $JacketFile, '--stage', '4',
            '--proof-out', $Proof0File, '--batch-out', $Batch1File,
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
        Assert-NotWritten -Stage 'collate asks the human' -Paths @($Proof0File, $Batch1File)
        foreach ($one in (Get-Content -LiteralPath $HumanReplacedFile -Raw | ConvertFrom-Json)) {
            Invoke-Checked -Stage "replace $($one.query) $($one.role) query" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $CopyFile[$one.role], '--address', $one.query,
                '--withdraw', '--instruction', 'query'
            ))
            foreach ($placed in $one.marks) {
                Invoke-Checked -Stage "replace $($one.query) $($one.role) at $($placed.address)" -CommandLine ($Launcher + @(
                    $Cmd.mark, '--edit-copy', $CopyFile[$one.role], '--address', $placed.address
                ) + @($placed.args) + @('--repo', $OriginalDir))
            }
        }
        Invoke-Checked -Stage 'check block-context replaced' -CommandLine ($Launcher + @(
            $Cmd.check, '--edit-copy', $CopyFile['block-context'], '--binder', $ReceivedFile['block-context'],
            '--human', $HumanFile
        ))
        Invoke-Checked -Stage 'collate' -Expect 4 -CommandLine $collateLine
        # Process #178, beside the main line: the same fixture written to a
        # second tree, gathered, and a copy seeded from that binder. Standing
        # in for ownership-context's own copy, it is one copy from another
        # tree, whose addresses answer to another address space, and the round
        # rolls back. The copy is unruled, so the report also carries one line
        # per place it left alone; what is asserted is the root line, the exit
        # code, and that nothing was written. The role's own copy is put back
        # once the refusal is read.
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
        Invoke-Checked -Stage 'other seed' -CommandLine ($Launcher + @(
            $Cmd.distribute, '--seed', '--binder', $OtherBinderFile,
            '--role', 'ownership-context', '--out', $OtherCopyFile
        ))
        Copy-Item -LiteralPath $CopyFile['ownership-context'] -Destination $KeptCopyFile
        Copy-Item -LiteralPath $OtherCopyFile -Destination $CopyFile['ownership-context']
        $mismatched = $Launcher + @(
            $Cmd.collate, '--jacket', $JacketFile, '--stage', '4',
            '--proof-out', $OtherProofFile,
            '--batch-out', $OtherBatchFile
        )
        $refused = Invoke-Checked -Stage 'collate from two trees refused' -Expect 1 -Capture -CommandLine $mismatched
        Copy-Item -LiteralPath $KeptCopyFile -Destination $CopyFile['ownership-context']
        $treeRefusal = $refused | Where-Object { $_.Contains('copy and binder name different gathered trees') }
        if (-not ($treeRefusal -match '/other' -and $treeRefusal -match '/original')) {
            Write-Host 'stage failed: collate from two trees refused'
            Write-Host 'expected a refusal naming the two trees; collate printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $mismatched)"
            exit 1
        }
        foreach ($written in @($OtherProofFile, $OtherBatchFile)) {
            if (Test-Path -LiteralPath $written) {
                Write-Host 'stage failed: collate from two trees refused'
                Write-Host "a rolled-back collate wrote $written"
                exit 1
            }
        }
        # Process #187, beside the main line: a move into a file the binder
        # never gathered, whose destination text drops a word of the
        # paragraph already there. A run of its own over a checkout holding
        # the four fixture files dispatches block-context alone; the plant
        # rules every slot of its copy clean but the move, and writes the
        # fifth file into the checkout `collate` reads. The fold measures the
        # destination against the page's paragraph, so the move's own row
        # refuses it and the round rolls back. What is asserted is that line,
        # the exit code, and that nothing was written.
        New-Item -ItemType Directory -Path $UngatheredDir | Out-Null
        Invoke-Checked -Stage 'ungathered fixture' -CommandLine @(
            'uv', 'run', 'python', '-c',
            $WriteFixtures,
            $UngatheredDir
        )
        Initialize-Checkout -Stage 'ungathered fixture' -Dir $UngatheredDir
        Invoke-Checked -Stage 'ungathered gather' -CommandLine ($Launcher + @(
            $Cmd.gather, '--repo', $UngatheredDir, '--out', $UngatheredBinderFile,
            (Join-Path $UngatheredDir 'fib.py'), (Join-Path $UngatheredDir 'rate.py'),
            (Join-Path $UngatheredDir 'store.py'), (Join-Path $UngatheredDir 'tally.py')
        ))
        New-Item -ItemType Directory -Path $UngatheredRun | Out-Null
        Invoke-Checked -Stage 'ungathered topology' -CommandLine ($Launcher + @(
            $Cmd.topology, '--build', '--binder', $UngatheredBinderFile, '--run', $UngatheredRun,
            '--ref', 'HEAD', '--repo', $UngatheredDir,
            'fib.py', 'rate.py', 'store.py', 'tally.py',
            '--stage', '4=block-context'
        ))
        Invoke-Checked -Stage 'ungathered open' -CommandLine ($Launcher + @(
            $Cmd.stage, 'open', '--jacket', $UngatheredJacketFile, '--stage', '4',
            '--repo', $UngatheredDir
        ))
        $ungatheredCopy = (Get-StageEntry -Name '4' -Jacket $UngatheredJacketFile).Copies[0]
        Invoke-Checked -Stage 'ungathered plant' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_ungathered_plant; write_ungathered_plant(Path(sys.argv[1]), Path(sys.argv[2]))',
            $ungatheredCopy, $UngatheredDir
        )
        $refusal = (& uv run python -c 'import sys; sys.path.insert(0, "scripts"); from smoke_fixture import UNGATHERED_REFUSAL; print(UNGATHERED_REFUSAL)')
        $ungathered = $Launcher + @(
            $Cmd.collate, '--jacket', $UngatheredJacketFile, '--stage', '4',
            '--proof-out', $UngatheredProofFile,
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
        foreach ($written in @($UngatheredProofFile, $UngatheredBatchFile)) {
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
    # fold left open: one agreed, two stetted and contested. No
    # slot is sent at an end of those moves, which are to come while their
    # placements are undecided. The answers leave b8 and c3 holding an add
    # beside another role's answer to it, a3, b9 and c1 with texts no role
    # has taken, the agreed move's two ends newly asked of the roles that
    # have not seen them, and the two contested moves, so places are carried forward
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
    # stays contested. The agreed move's ends are asked here: its arrival at
    # store.py@b8 is cleaned and settles, and its empty remainder at
    # store.py@b9 is held against the rewording. Every other place the batch asks about is one
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
    # tally.py@b1's takes the mover's side, which agrees the move and leaves
    # both ends carried forward: the move's remainder at the origin is a
    # text the roles that cleaned it have not seen, and at the destination
    # its arrival composes with function-context's correction into one
    # they have not seen either. So the call commits its proof and exits 3,
    # as `collate` does with a place composed. The same call takes in the changes and the two moves only their
    # proposer read, which no turn was run for (Process #385); taking each
    # move in settles both its ends (Process #388). The second call takes that
    # proof and dispositions-ends.json, `ENDS`, which rules the two ends, and
    # closes the proof with exit 0. The stage closes on that proof; until it
    # does, the stage reading its revise is refused, since the stage's own
    # `reads` decides the tree rather than a path typed here.
    disposition = {
        Invoke-Checked -Stage 'disposition placements' -Expect 3 -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $TurnTwoProofFile,
            '--dispositions', $DispositionsFile, '--proof-out', $PlacedFile
        ))
        Invoke-Checked -Stage 'disposition ends' -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $PlacedFile,
            '--dispositions', $EndsFile, '--proof-out', $FinalFile
        ))
        $early = $Launcher + @(
            $Cmd.stage, 'open', '--jacket', $JacketFile, '--stage', $SecondStage,
            '--repo', $OriginalDir
        )
        $refused = Invoke-Checked -Stage 'stage open 5 before 4 closes refused' -Expect 1 -Capture -AndErrors -CommandLine $early
        if (-not (($refused -join "`n").Contains('not closed'))) {
            Write-Host 'stage failed: stage open 5 before 4 closes refused'
            Write-Host 'expected a refusal naming the stage that has not closed; stage open printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $early)"
            exit 1
        }
        Invoke-Checked -Stage 'stage close 4' -CommandLine ($Launcher + @(
            $Cmd.stage, 'close', '--jacket', $JacketFile, '--stage', '4', '--proof', $FinalFile
        ))
    }
    # `stage open 5` builds the second stage's tree: a worktree of the
    # pre-edit commit with the first stage's closed proof set over it through
    # the write end, so a docket the write end refuses stops the smoke here.
    # The diff is the assertion: `write_expected` writes the text
    # smoke_fixture.py says the plant makes land, and git compares each page
    # with the tree's, with core.autocrlf off so a line ending that differs is
    # a difference. Exit 0 means the first stage set exactly what was planted.
    # On a difference it also prints the original against the tree, so a
    # reader sees what the chain did.
    diff = {
        Invoke-Checked -Stage 'stage open 5' -CommandLine ($Launcher + @(
            $Cmd.stage, 'open', '--jacket', $JacketFile, '--stage', $SecondStage,
            '--repo', $OriginalDir
        ))
        $root = (Get-StageEntry -Name $SecondStage).Root
        New-Item -ItemType Directory -Path $ExpectedDir | Out-Null
        Invoke-Checked -Stage 'expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_expected; write_expected(Path(sys.argv[1]))',
            $ExpectedDir
        )
        foreach ($page in (Get-ChildItem -LiteralPath $ExpectedDir -File)) {
            $set = Join-Path $root $page.Name
            Invoke-Checked -Stage "diff $($page.Name)" -CommandLine @(
                'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
                $page.FullName, $set
            ) -OnFailure {
                Write-Host 'what the chain did -- the original against the tree:'
                & git -c core.autocrlf=false --no-pager diff --no-index -- (Join-Path $OriginalDir $page.Name) $set | Out-Host
            }
        }
    }
    # The second stage, which reads what the first one closed on. Its row
    # says `reads = "revise:4"`, so the tree `stage open` built for it at the
    # diff stage is the first stage's closed proof set over the pre-edit
    # commit, and its binder is gathered there: the addresses are the
    # revise's own and not the original's. The one role corrects a paragraph
    # the first stage already corrected, so the correction is measured
    # against the revised text. Every other prose place is cleaned -- fib.py's
    # from the plant's list, and the scope's other pages as the copy holds
    # them, since the stage's binder holds the whole scope -- and the diff at
    # the compacting stage, in the tree that stage opens on, is what says the
    # revise still carries the paragraphs nobody changed.
    second = {
        $entry = Get-StageEntry -Name $SecondStage
        $secondCopy = $entry.Copies[0]
        $root = $entry.Root
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
            '--cite', 'fib.py:1', '--repo', $root
        ))
        $secondClean = Get-Content -LiteralPath (Join-Path $Run 'second-clean.json') -Raw | ConvertFrom-Json
        $others = @((Get-Content -LiteralPath $secondCopy -Raw | ConvertFrom-Json).sheets |
            ForEach-Object { $_.marks } | ForEach-Object { $_.address } |
            Where-Object { -not $_.StartsWith('fib.py@') })
        foreach ($address in @($secondClean) + $others) {
            Invoke-Checked -Stage "second clean $address" -CommandLine ($Launcher + @(
                $Cmd.mark, '--edit-copy', $secondCopy, '--address', $address,
                '--instruction', 'clean', '--cite', "$(($address -split '@')[0]):1", '--repo', $root
            ))
        }
        Invoke-Checked -Stage 'second check' -CommandLine ($Launcher + @(
            $Cmd.check, '--edit-copy', $secondCopy, '--binder', $entry.Received[0]
        ))
        # One role read the place, so its change goes to the chief with no
        # turn to run (Process #385): collate carries it forward and exits 3,
        # writing no batch, and `disposition` takes the change in from
        # second-dispositions.json. The stage closes on that proof.
        Invoke-Checked -Stage 'second collate' -Expect 3 -CommandLine ($Launcher + @(
            $Cmd.collate, '--jacket', $JacketFile, '--stage', $SecondStage,
            '--proof-out', $SecondCollatedFile, '--batch-out', $SecondBatchFile
        ))
        Assert-NotWritten -Stage 'second collate' -Paths @($SecondBatchFile)
        Invoke-Checked -Stage 'second disposition' -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $SecondCollatedFile,
            '--dispositions', (Join-Path $Run 'second-dispositions.json'),
            '--proof-out', $SecondProofFile
        ))
        Invoke-Checked -Stage 'stage close 5' -CommandLine ($Launcher + @(
            $Cmd.stage, 'close', '--jacket', $JacketFile, '--stage', $SecondStage,
            '--proof', $SecondProofFile
        ))
    }
    # The compacting stage (Process #193), reading the second stage's revise
    # as its row says, since a jacket's stages are one chain. `stage open`
    # builds that tree, and the second stage's diff is read there first:
    # fib.py is what `write_second_expected` writes and every other page is
    # as the first stage left it. The stage is dealt the `b` and `c` places
    # over its cap and nothing else -- the two in store.py's last function,
    # whose prose the plant wrote on both sides of the cap -- and the copy is
    # what says so -- with rate.py@b1, three lines as the first stage left it,
    # since the stage's binder holds the whole scope. The role condenses one
    # of store.py's with a `patch` quoting the whole paragraph and leaves the
    # other two at length with a `clean` carrying the reason, which is what
    # compact.md asks of a paragraph that cannot come under the cap. A
    # `correct` there is refused by `mark`, naming the stage.
    compacting = {
        $plant = Get-Content -LiteralPath $CompactingFile -Raw | ConvertFrom-Json
        Invoke-Checked -Stage 'stage open 6' -CommandLine ($Launcher + @(
            $Cmd.stage, 'open', '--jacket', $JacketFile, '--stage', $CompactingStage,
            '--repo', $OriginalDir
        ))
        $entry = Get-StageEntry -Name $CompactingStage
        $root = $entry.Root
        $secondRoot = (Get-StageEntry -Name $SecondStage).Root
        New-Item -ItemType Directory -Path $SecondExpectedDir | Out-Null
        Invoke-Checked -Stage 'second expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_second_expected; write_second_expected(Path(sys.argv[1]))',
            $SecondExpectedDir
        )
        foreach ($page in (Get-ChildItem -LiteralPath $ExpectedDir -File)) {
            $want = Join-Path $SecondExpectedDir $page.Name
            if (-not (Test-Path -LiteralPath $want)) {
                $want = $page.FullName
            }
            $set = Join-Path $root $page.Name
            Invoke-Checked -Stage "second diff $($page.Name)" -CommandLine @(
                'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
                $want, $set
            ) -OnFailure {
                Write-Host 'what the second stage did -- the revise against its tree:'
                & git -c core.autocrlf=false --no-pager diff --no-index -- (Join-Path $secondRoot $page.Name) $set | Out-Host
            }
        }
        $copy = $entry.Copies[0]
        $held = Get-Content -LiteralPath $copy -Raw | ConvertFrom-Json
        # The deal is the assertion: the copy holds a slot at each place over
        # the cap and at no other, so a stage dealt everything, or nothing,
        # fails here rather than at the diff.
        $slots = @($held.sheets | ForEach-Object { $_.marks } | ForEach-Object { $_.address })
        if (($slots -join ',') -ne ($plant.dealt -join ',')) {
            Write-Host 'stage failed: stage open 6'
            Write-Host "expected slots at $($plant.dealt -join ', '); the copy holds: $($slots -join ', ')"
            Write-Host "copy: $copy"
            exit 1
        }
        if ($held.stage -ne $CompactingStage) {
            Write-Host 'stage failed: stage open 6'
            Write-Host "the copy names stage '$($held.stage)', not '$CompactingStage'"
            exit 1
        }
        # The widened copy, taken before the two rulings below: a role that
        # adds `correct` to its own copy's `admits` gets it past `mark`,
        # which reads that field, so `collate` is what holds the marks to the
        # stage's row. It stands in for the stage's own copy while `collate`
        # reads it, and the copy the stage returns is put back untouched.
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
            '--repo', $root
        ))
        Invoke-Checked -Stage 'widened clean placed' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $WidenedCopyFile, '--address', $plant.kept,
            '--instruction', 'clean', '--reason', $plant.reason, '--cite', "$(($plant.kept -split '@')[0]):1", '--repo', $root
        ))
        Invoke-Checked -Stage 'widened rate clean placed' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $WidenedCopyFile, '--address', $plant.rate_kept,
            '--instruction', 'clean', '--reason', $plant.rate_reason, '--cite', "$(($plant.rate_kept -split '@')[0]):1", '--repo', $root
        ))
        Copy-Item -LiteralPath $copy -Destination $KeptCompactingCopyFile
        Copy-Item -LiteralPath $WidenedCopyFile -Destination $copy
        $widened = $Launcher + @(
            $Cmd.collate, '--jacket', $JacketFile, '--stage', $CompactingStage,
            '--proof-out', $WidenedProofFile
        )
        $refused = Invoke-Checked -Stage 'collate over a widened copy refused' -Expect 1 -Capture -CommandLine $widened
        Copy-Item -LiteralPath $KeptCompactingCopyFile -Destination $copy
        if (-not (($refused -join "`n").Contains("stage $CompactingStage admits"))) {
            Write-Host 'stage failed: collate over a widened copy refused'
            Write-Host 'expected a refusal naming the stage and what it admits; collate printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $widened)"
            exit 1
        }
        Assert-NotWritten -Stage 'collate over a widened copy refused' -Paths @($WidenedProofFile)
        Invoke-Checked -Stage 'compacting patch' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $copy, '--address', $plant.patched,
            '--instruction', 'patch',
            '--cite', "$(($plant.patched -split '@')[0]):1",
            '--from', "@$(Join-Path $Run 'compacting-from.txt')",
            '--to', "@$(Join-Path $Run 'compacting-to.txt')",
            '--reason', 'three lines state what two state, and the cap is two',
            '--repo', $root
        ))
        Invoke-Checked -Stage 'compacting clean' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $copy, '--address', $plant.kept,
            '--instruction', 'clean', '--reason', $plant.reason, '--cite', "$(($plant.kept -split '@')[0]):1", '--repo', $root
        ))
        Invoke-Checked -Stage 'compacting rate clean' -CommandLine ($Launcher + @(
            $Cmd.mark, '--edit-copy', $copy, '--address', $plant.rate_kept,
            '--instruction', 'clean', '--reason', $plant.rate_reason, '--cite', "$(($plant.rate_kept -split '@')[0]):1", '--repo', $root
        ))
        # The instruction the row does not admit. `mark` refuses it as it
        # places, so the copy is left exactly as the two rulings above left
        # it -- which the check below is what proves.
        $notAdmitted = $Launcher + @(
            $Cmd.mark, '--edit-copy', $copy, '--address', $plant.patched,
            '--instruction', $plant.refused,
            '--false', 'Nothing is ever', '--true', 'Nothing is',
            '--reason', 'the sentence reads shorter', '--cite', 'store.py:40',
            '--repo', $root
        )
        $refused = Invoke-Checked -Stage 'compacting correct refused' -Expect 1 -Capture -CommandLine $notAdmitted
        if (-not (($refused -join "`n").Contains("stage $CompactingStage admits"))) {
            Write-Host 'stage failed: compacting correct refused'
            Write-Host 'expected a refusal naming the stage and what it admits; mark printed:'
            $refused | Out-Host
            Write-Host "command: $(Format-CommandLine $notAdmitted)"
            exit 1
        }
        # The binder the role received holds the dealt places alone, and is
        # the one `check` reads (references/compact.md).
        Invoke-Checked -Stage 'compacting check' -CommandLine ($Launcher + @(
            $Cmd.check, '--edit-copy', $copy, '--binder', $entry.Received[0],
            '--repo', $root
        ))
        # One role read each place, so the patch goes to the chief with no
        # turn to run, as any lone change does (Process #385, #387): collate
        # carries it forward and exits 3, and `disposition` takes it in from
        # compacting-dispositions.json. The stage closes on that proof.
        Invoke-Checked -Stage 'compacting collate' -Expect 3 -CommandLine ($Launcher + @(
            $Cmd.collate, '--jacket', $JacketFile, '--stage', $CompactingStage,
            '--proof-out', $CompactingCollatedFile
        ))
        Invoke-Checked -Stage 'compacting disposition' -CommandLine ($Launcher + @(
            $Cmd.disposition, '--proof', $CompactingCollatedFile,
            '--dispositions', (Join-Path $Run 'compacting-dispositions.json'),
            '--proof-out', $CompactingProofFile
        ))
        Invoke-Checked -Stage 'stage close 6' -CommandLine ($Launcher + @(
            $Cmd.stage, 'close', '--jacket', $JacketFile, '--stage', $CompactingStage,
            '--proof', $CompactingProofFile
        ))
    }
    # `proof --jacket` sets the whole run once every stage has closed: the
    # pre-edit commit's tree with each stage's closed proof set over it in
    # topology order, into $ProofDir, which must not exist yet and holds only
    # the pages a proof set. The diff is against the first stage's expected
    # pages with the second stage's fib.py and the compacting stage's
    # store.py written over them; no later stage opens on the compacting
    # stage's tree, so this is where its page is read. On a difference it
    # also prints the original against the proof.
    proof = {
        Invoke-Checked -Stage 'proof' -CommandLine ($Launcher + @(
            $Cmd.proof, '--jacket', $JacketFile, '--repo', $OriginalDir, '--out', $ProofDir
        ))
        New-Item -ItemType Directory -Path $CompactingExpectedDir | Out-Null
        Invoke-Checked -Stage 'compacting expected' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_compacted_expected; write_compacted_expected(Path(sys.argv[1]))',
            $CompactingExpectedDir
        )
        New-Item -ItemType Directory -Path $ProofExpectedDir | Out-Null
        foreach ($dir in @($ExpectedDir, $SecondExpectedDir, $CompactingExpectedDir)) {
            Copy-Item -Path (Join-Path $dir '*') -Destination $ProofExpectedDir -Force
        }
        Invoke-Checked -Stage 'proof diff' -CommandLine @(
            'git', '-c', 'core.autocrlf=false', '--no-pager', 'diff', '--no-index', '--',
            $ProofExpectedDir, $ProofDir
        ) -OnFailure {
            Write-Host 'what the run did -- the original against the proof:'
            & git -c core.autocrlf=false --no-pager diff --no-index -- $OriginalDir $ProofDir | Out-Host
        }
    }
    # The partial approval, beside the main line and over the same closed
    # run (ruling #192): the author approved two of the first stage's decided
    # places, so `proof --jacket --only` sets those and nothing else. Its
    # revise holds `store.py` alone -- the only page those two places sit on
    # -- and the diff is against a page written by hand as the fixture with
    # those two places set, so a run that set a third place, or set neither,
    # fails here. A second approval names one end of the agreed move alone,
    # which is refused.
    partial = {
        Invoke-Checked -Stage 'plant-approval' -CommandLine @(
            'uv', 'run', 'python', '-c',
            'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; from smoke_fixture import write_approval; write_approval(Path(sys.argv[1]))',
            $Run
        )
        $approval = Get-Content -LiteralPath $ApprovalFile -Raw | ConvertFrom-Json
        # An approved place is named with the stage that decided it.
        $only = @()
        foreach ($address in $approval.approved) {
            $only += @('--only', "4:$address")
        }
        Invoke-Checked -Stage 'partial approval' -CommandLine ($Launcher + @(
            $Cmd.proof, '--jacket', $JacketFile, '--repo', $OriginalDir
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
        # One end of the agreed move alone. A move is approved whole or not
        # at all (Process #283), so `proof --only` refuses it, naming the
        # move, and writes nothing.
        $oneEnd = $Launcher + @(
            $Cmd.proof, '--jacket', $JacketFile, '--repo', $OriginalDir,
            '--only', "4:$($approval.'one-end')", '--out', $OneEndDir
        )
        $refused = Invoke-Checked -Stage 'one end refused' -Expect 1 -Capture -AndErrors -CommandLine $oneEnd
        Assert-Lines -Stage 'one end refused' -Printed $refused -CommandLine $oneEnd -Expected @(
            'copy-chief store.py@b9 -> store.py@b8: approve both ends of this move together'
        )
        Assert-NotWritten -Stage 'one end refused' -Paths @($OneEndDir)
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
        # A stage that fails exits above, so this line names a section that
        # ran to its end; the full-run gate reads one per section.
        Write-Host "section passed: $stageName"
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
