# The middle chain smoke: proving the commands compose before an agent runs them

Design, 2026-09-08. Brainstormed with Roy the same day.

## What this is for

The middle of the chain has never been run end to end by anything but an agent, and the one
recorded live run lost a finding without saying so. This builds a script that drives every
command in the middle from `gather` to `proof`, with every decision planted in advance, so the
chain can be shown to compose before an agent's reasoning is added to it.

Roy, 2026-09-08: *"we can script a few of these in a Bash or Powershell script to verify that the
system works just by being able to call the correct commands all the way through. That leaves the
agent's ability to reason out of it. We can compose the different decisions without explicitly
caring that the decisions are true and accurate of a piece of text. A really large smoke test."*

## The four bars

A run passes when all four hold. They were settled in conversation on 2026-09-08.

| | |
| --- | --- |
| **Nothing is lost** | every mark reaches the proof, or is refused out loud with a reason naming it |
| **Nothing refuses falsely** | no stage stops on something that is not a real defect |
| **No finagling** | the chain runs from its own invocations, with nobody diagnosing a stage and re-issuing it |
| **The result reads as a diff** | `git diff` of the original tree against the proof arrives at the expected changes |

The third is the reason this script exists. It is not a property anyone can inspect; it is
demonstrated by something other than a person driving the chain from one end to the other.

## What is out of scope, and deliberately

- **Stage 7b and `prove_unchanged`.** The proof is real files and the diff is the original
  against it. Nothing here writes over the repository's own files. Ruled 2026-09-07 and
  restated 2026-09-08.
- **Agent reasoning.** Whether a decision is true of the text is not this script's question. The
  planted clauses may be single letters, so long as what lands is a well-formed comment.
- **Bad input.** The script assumes the tools were used correctly. Roy, 2026-09-08: *"we are
  going to skip the part where they don't use the tool correctly as we will have code and tests
  to show that bad places get refused."* Refusals belong in unit tests that prove they fire.
- **A second language.** The fixture is Python only. Walking the lexical tier as well as the
  tokenized one would test the tier dispatch, which is a known fragile spot, but it costs the
  readability of a fixture whose whole value is being short enough to see. Deferred on purpose
  rather than overlooked.

## The instrument

**A PowerShell script under `scripts/`, driving the real console face.** Not a pytest calling
`main()` directly. `tests/test_the_chain.py` already does that for four of the commands, and it
is weaker evidence for the third bar: an agent invokes
`python <skill>/scripts/comment-review.py ...` through a shell, so a chain proved only through
`main()` leaves the argument parsing and the shell boundary untested.

**Every multi-line value goes through a file, every scalar through a flag.** The script writes
its planted comment text and passes `@path`, per `decision-log.md Process: #103`. Nothing a shell
eats crosses a command line, which keeps this inside the repo's no-heredoc rule rather than
needing an exception.

**It exits nonzero at the first stage that refuses,** naming the stage and printing the command,
so a failure carries its own reproduction.

## The fixture

A tree the script writes, not this repository. Two Python files, each short enough to read whole.
`fib.py` carries the scenario rows below; `rate.py`, added 2026-09-11, carries the options
`fib.py` had no free place for -- a `patch`, a `query` of shape `unable-to-determine`, and a
composition -- and puts a second page in the docket. `fib.py`:

```python
"""Fibonacci, counted so the recursion can be seen."""

import functools

# Module state, written by the wrapper and read by the caller.
CALLS = 0  # every entry, memoised or not


def logged(fn):
    """Count each call and pass it through."""

    @functools.wraps(fn)
    def wrapper(n):
        global CALLS
        CALLS += 1  # the decorator's whole job
        return fn(n)

    return wrapper


# The cache sits inside the decorator stack on purpose: logged sees
# every call, cache sees only the misses.
@logged
@functools.cache
def fib(n):
    """The nth Fibonacci number, counting from fib(0) = 0."""
    if n < 2:  # base case
        return n
    # Two calls per level, which is what the counter measures.
    return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    print(fib(10), CALLS)
```

### What it yields

Read off the page builder itself, `flows/page_for.page_of`, on 2026-09-11 -- the first draft of
this table was written from memory and was wrong in two rows.

| series | what the fixture gives it |
| --- | --- |
| `a` | four places: `a0` the module docstring, `a1` `logged`, `a3` `fib`, and **`a2` `wrapper` with none**, the empty declaration an `add` can fill |
| `b` | eighteen places, three filled: `b1`, **the two-line run at `b9`** above the decorator stack, and `b14` **inside `fib`'s body**. The rest are empty, `b8` above `return wrapper` among them |
| `c` | seventeen places, one per code line, three filled: `c1`, and two **inside a function body** -- `c6` in `wrapper`, `c12` in `fib` |
| `f` | two places, **both empty**: `f0` at the head, since the module docstring is `a0`, and `f1` at the end of file, since the dunder-main block is code at `b15` and `b16` |

**Leading is not a series here, and not a place.** It takes a symbol and never an address --
`Addressing: #4` and `#5` -- so it appears in `page.leading` rather than in `page.cues.places`:
seven of them, `d0` to `d6`, which a drop has to resolve.

Three shapes in it are edge cases rather than decoration: **two stacked decorators**, so the
anchor of a declaration is not its `def` line; **a nested `def` inside a function body**, which
is the position `module-context` declined 39 times on the 2026-09-07 run; and **an empty foot**,
`f1` and the closing gap `b17` after the dunder-main block, where an `add` exercises
`Addressing: #19`'s rule that at the foot the leading goes on the other side.

Each series carries more than one member on purpose. A series of one never exercises its
ordinals, and the first two drafts of this fixture had exactly that fault -- a single `c` and no
filled `b` at all.

## The scenario matrix

Every planted address exercises one path through the middle. Clean appears only where the point
is that a clean is recorded; a page of cleans proves nothing about resolution.

| what is planted | what it proves |
| --- | --- |
| one role marks, the other three defer with `query outside-my-role` | the fold settles a place on its own, without the chief |
| two roles `correct` one address differently | the disagreement is carried forward rather than silently resolved |
| three roles disagree at one address | the fold handles more than a pair |
| chief `taken_in`, side a role | a role's text reaches the proof, attributed |
| chief `taken_in`, side `original` | the original stands, which is `stet`'s effect |
| chief `recast` with its own prose | text neither role proposed reaches the proof |
| a `drop` | a place is vacated and the leading resolves |
| an `add` at an empty place | the case that vanished on the 2026-09-07 run |
| a `move` | one mark becoming two alterations, origin and destination |
| a `query` no role can settle | it rides to the end and is printed, not ruled |
| a `patch` beside a `query unable-to-determine` (`rate.py`) | the patch settles alone; the abstaining query stays out of the fold |
| a composition: two roles correct two sentences of one paragraph (`rate.py`) | the fold combines them, and the combined text reaches the proof |
| one turn, every answer planted (Task 12) | the turn loop folds each of `hold`, `withdraw`, `correct`, `patch`, `clean` and `query` |
| **the addresser lookup feeding an `add`** | a place found by file and line, its returned address used to add, and the comment present in the proof |

The last row is the positive form of the defect that lost a finding, and it pulls `addresser`
into the chain, which the eight-command sequence otherwise never touches.

Roy, 2026-09-11, on why every option is planted: *"Thats why it can't be partially done. The
options need to be exercised."*

## The chain the script drives

As `SKILL.md` names it:

```
gather -> topology --build -> topology --verify -> distribute
  -> [mark, once per ruling, per role] -> check x4
  -> collate -> [one turn: answers, check --answers x4, turn] -> disposition -> proof
```

One turn runs between `collate` and `disposition`, added 2026-09-11 (Task 12) when a hand-run
turn found the re-read half of the loop broken, which no run had reached while the baseline ran
none. The disposition then closes the proof at turn 1.

## What it asserts

Two things, and nothing else. Roy, 2026-09-08: *"Really i would go just for start here end there
no errors. Counting artifacts and other things in between makes it more complicated and brittle
than it needs to be. Those are testing implementation details not api functionality."*

It held when a review showed its cost: a row planted to escalate can re-read instead, and while
another row escalates, `collate` still exits 4 and nothing in the script notices. Asked on
2026-09-11 whether the rule still stands (`smoke-middle-script` T24), Roy: *"yes because the
only thing that matters is that the workflow works from end-to-end not if the middle things
don't work as expected. If the middle things are not doing what they are supposed to do then
that becomes an actual pytest test"*.

**Exit codes.** Every stage exits 0 on planted-correct input, except `collate`, which exits the
code the plant predicts. Its exit codes are a contract (`commands/collate.py`): 3 when places are
carried forward for a re-read, 4 when any is an escalation, which outranks a re-read. The matrix
plants disagreements on purpose, so the script expects exactly 4 there and fails on any other
code. A stage stopping is the second bar failing.

Corrected 2026-09-11, before Task 9, from a hand probe and two rulings by Roy. The first row of
the matrix read "one role marks, the other three clean". Under `Process: #89` a lone mark is sent
back to every role that marked the place, so three cleans carry it forward rather than letting
it settle. With the other three deferring by `query outside-my-role`, it settles alone. And this
paragraph said every stage exits 0, which the matrix's own disagreements make `collate` refuse to
do.

**The diff, exactly.** The script planted every decision, so it knows what the proof must
contain. It compares the original tree with the proof and requires that every planted change is
present, in the right place, and that nothing else moved.

**The diff is also the loss detector**, which is why nothing counts marks in between. A mark
that goes missing anywhere in the chain arrives as a planted change absent from the diff. An
intermediate count would be a second detector for what the first one already sees, bought at the
price of asserting on the shape of `proof0.json` and the chief's copy -- implementation detail
that belongs in unit tests, where it can be dropped when it stops earning its place.

**And nothing reads stdout.** Stage output is prose, and prose in a prototype changes wording; a
script asserting on a sentence breaks on edits that broke nothing.

## Coupling, and the fact that this is provisional

**Command names live in one table at the top**, so a renamed command touches one row rather
than a dozen call sites. Flags are written at each call site: each stage calls its command in
one place, and a renamed flag touches only the calls that pass it (Roy, 2026-09-11,
`smoke-middle-script` T12). The chief's command was `cap` while this was being written and
is `disposition` as of 2026-09-08, `Vocabulary: #36`.

**It asserts on exit codes and the diff. Nothing else.** Not wording, not intermediate artifacts,
not file layout beyond what the commands are told to write, not ordering the commands do not
promise. Every one of those is a way to couple a durable test to a prototype's insides.

**The script is provisional and the spec says so.** Roy, 2026-09-08: *"while it is a good thing
to build it is also building against a prototype so be careful of the tight coupling. When this
passes and agents can run it on an actual repo we can review and decide it is needs to be not a
prototype."* It is a rung. Nothing else should grow to depend on it, and it is allowed to be
thrown away when the surface it drives is settled.

**A run leaves no permanent code changes inside the repo.** Its outputs -- the fixture, the
binder, the copies, the proof -- go to a run directory outside it. Python's own gitignored
`__pycache__` folders are not a run output and are allowed. An earlier brief said a run writes
nothing inside the repo; Roy, 2026-09-11, ruling on `smoke-middle-script` T19: *"it was a stupid
absolute literal statement. It should have been leaves no permanent code changes inside of the
repo"*.

**The script never deletes a run directory.** Its outputs stay where they are, so a run that
breaks can be inspected, and they are removed by hand when no longer needed. Roy, 2026-09-11,
ruling on `smoke-middle-script` T66: *"Neither the script doesn't drop anything. We drop the
outputs manually when we are ready"*.

## The order: the fixes first, the script second

Roy, 2026-09-08: *"Write it second because we do not want to confuse it with a TDD design
system."*

The known defects are repaired first, and the script is written against a chain we already
believe works. Written first it would fail four times on things already filed, and those failures
would read as a red-green cycle -- which would invite deriving the fixes from what the script
reports rather than from the rulings that already specify them. It is a verification instrument,
not a design driver. Its first real run should be against a chain nobody expects it to break, so
that anything it stops on is new.

## What it is expected to surface

Four known defects are inside its path. They are repaired before it is written, per the order
above, and they are listed here because they are what the script would have caught had it existed
on 2026-09-07:

- `disposition` writing every recast as `correct`, so a recast of an `add` at an empty place writes
  nothing and exits 0.
- The leading disagreement between the brief and the setter.
- `fill` seeding a mark from the role's own entry where the copy has no slot.
- The address checks that are absent at `mark` and at `check`.

Anything else it stops on is new, and is a defect with a reproduction attached.

## After it passes

The instructions are reseeded against the command surface it proves, and the four roles are
dispatched live on a real repository. Roy, 2026-09-08: *"My deferral was only deferred until we
have some idea of what commands can be called. We will reseed the instructions and try it with
the new instructions."* That run is the baseline, and this script is what makes its failures
attributable to the agents rather than to the chain.
