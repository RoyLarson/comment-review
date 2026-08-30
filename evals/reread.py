"""T50 -- the same judge reads one artifact twice, and the letters are compared.

!! THIS ASKS WHETHER THE INSTRUMENT IS STABLE, NOT WHETHER IT IS RIGHT. Roy,
2026-08-29 (`decision-log.md Process: #56`): *"just because there is variance in
the result doesn't make the measure invalid it makes it uncertain. A repeat or
three or four or five off the same result fixes the variance."* **Variance is
reducible by N; validity is not reducible by anything.** So a disagreement found
here sets the sample size a later run needs -- it does not condemn the grader,
and it is not evidence about whether the grade is correct.

! WHICH IS WHY IT COMES BEFORE CALIBRATION. Calibrating on the END tree (C3/T51)
asks whether the human's own fix scores at the top; that question cannot be
answered from one sample if the same input returns different letters. Stability
is the precondition, and this module is the only thing that measures it.

!! IT COMPARES AND DOES NOT AVERAGE, for the reason `grader.py` gives for having
no `aggregate()`: a mean over A=4, B=3, C=2 asserts the A-to-B distance equals
the B-to-C distance, which nothing establishes. **Equality is the only operation
these letters support**, so the whole comparison is "were they the same", stated
per axis and once overall.

! THE RUNS ARE NOT INDEPENDENT SAMPLES OF A CASE -- they are repeated readings of
ONE artifact. Nothing here re-runs a reviewer, so a disagreement is the judge's
alone and cannot be a difference in what was filed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import grader

#: Every field a comparison is drawn over -- the five graded axes, plus the
#: overall the judge reports separately. ! `reader_value` is NOT here: it is
#: recorded and not graded (`rubric.md`), so it carries no letter to compare,
#: and `unkeyed_claims` is an itemised list rather than a grade.
COMPARED = [*grader.AXES, "overall"]

#: The grade meaning "this axis could not be scored at all".
UNGRADED = "N/A"

#: The axes scored against the answer key, which are `N/A` without one.
#: MEASURED 2026-08-29: with no END, all three came back `N/A` in both readings
#: and the run bought one axis of stability for the price of five.
KEYED_AXES = ["detection", "diagnosis", "prescription"]

#: What two readings of this case cost, MEASURED 2026-08-29: **$0.61 for two**,
#: at `claude-opus-5` with a ~32,000-character prompt and `max_tokens=16000`.
#: ! Recorded because `--runs` is chosen by a human who is paying, and "a few
#: cents" was the guess it replaced.
COST_PER_READING = "about $0.30"


class NotAComparison(Exception):
    """Fewer than two readings, which cannot show agreement or disagreement."""


def letters(judged: dict) -> dict:
    """The graded letters of one reading, flattened to field -> letter.

    ! THE REASONS ARE LEFT BEHIND ON PURPOSE. They are kept in full in the
    written artifact, because `decision-log.md Process: #56` says the reason is
    the data; what this returns is only the part two readings can be compared on.
    """
    flat = {axis: judged["axes"][axis]["grade"] for axis in grader.AXES}
    flat["overall"] = judged["overall"]
    return flat


def compare(readings: list[dict]) -> dict:
    """Per field: the letters in run order, whether it was measured, whether it held.

    ! ORDER IS PRESERVED so a reader can see WHICH run said what. A set would
    answer "did they agree" and lose the ability to say anything else.

    !! AN AXIS EVERY READING SCORED `N/A` IS NOT MEASURED, AND MUST NOT COUNT AS
    AGREEMENT -- this returned `agreed: True` for those until the first live run
    exposed it, 2026-08-29. **A field that cannot vary cannot disagree**, so
    counting it makes the instrument look stabler exactly where it learned
    nothing. That is `docs/gates.md`'s own case arriving from the inside: the
    699/699 round trip scored perfectly because it compared a file with itself.

    ! MEASURED, on the first run: three of six fields were `N/A` in BOTH
    readings, because the case supplies no END and `detection`, `diagnosis` and
    `prescription` are all scored against the key. Counted the old way that read
    as four of six holding; counted honestly it is one of three.

    ! `N/A` AGAINST A LETTER IS A DISAGREEMENT, NOT AN ABSENCE. The readings
    then differ about whether the axis was gradeable at all, which is a real
    instability and one of the more interesting kinds.
    """
    if len(readings) < 2:
        raise NotAComparison(
            f"{len(readings)} reading(s): a comparison needs at least two."
        )
    seen = [letters(r) for r in readings]
    out = {}
    for field in COMPARED:
        got = [s[field] for s in seen]
        measured = not all(g == UNGRADED for g in got)
        out[field] = {
            "letters": got,
            "measured": measured,
            # ! `None`, NOT `True`, when nothing was measured. A boolean here
            # is read as a verdict no matter what the neighbouring flag says.
            "agreed": (len(set(got)) == 1) if measured else None,
        }
    return out


def reread(
    *,
    findings: pathlib.Path,
    under_review: pathlib.Path,
    start: str,
    end: str,
    end_diff: str,
    mechanical: dict,
    arm: str,
    eval_id: str,
    runs: int = 2,
    client=None,
    max_tokens: int = grader.MAX_TOKENS,
    keep: pathlib.Path | None = None,
) -> dict:
    """Grade one artifact `runs` times and report whether the letters held.

    ! EVERY READING GETS AN IDENTICAL PROMPT. `grader.build_prompt` is a pure
    function of these arguments, so the only thing that varies between runs is
    the model's own sampling -- which is the quantity being measured.

    ! ONE CLIENT ACROSS ALL RUNS, so a difference cannot be a difference in how
    the request was constructed.

    ! A FAILED RUN PROPAGATES rather than shortening the set. Comparing the runs
    that happened to succeed would report agreement over a sample chosen by which
    calls did not raise.

    !! BUT EACH READING IS WRITTEN TO `keep` AS IT LANDS, BECAUSE PROPAGATING
    MUST NOT ALSO DISCARD. MEASURED 2026-08-29: a `--runs 5` died on a truncated
    answer and wrote nothing at all, so every reading that had already been paid
    for went with it. **The refusal is about what may be COMPARED; it was never
    about throwing away what was bought.** A later run can read these back.
    """
    if runs < 2:
        raise NotAComparison(f"runs={runs}: a comparison needs at least two.")

    client = client or grader._client()
    graded = []
    for n in range(1, runs + 1):
        # ! NOT A COMPREHENSION ANY MORE, so a partial result exists to save.
        one = grader.grade(
            findings=findings,
            under_review=under_review,
            start=start,
            end=end,
            end_diff=end_diff,
            mechanical=mechanical,
            arm=arm,
            eval_id=eval_id,
            client=client,
            max_tokens=max_tokens,
        )
        graded.append(one)
        if keep is not None:
            keep.mkdir(parents=True, exist_ok=True)
            (keep / f"reading-{n}.json").write_text(
                json.dumps(one, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    fields = compare([g["editorial"] for g in graded])
    return {
        "eval_id": eval_id,
        "arm": arm,
        "model": grader.MODEL,
        "rubric_version": grader.RUBRIC_VERSION,
        "runs": runs,
        # ! STATED, NOT LEFT TO BE DERIVED. T50 asks that whether they agree is
        # said, so a reader is never diffing two lists to find out.
        #
        # !! OVER THE MEASURED FIELDS ALONE. Including the `N/A` ones let three
        # vacuous agreements outvote two real disagreements on the first live
        # run -- the instrument reporting stability it had not observed.
        "agreed": all(f["agreed"] for f in fields.values() if f["measured"]),
        # ! THE DENOMINATOR TRAVELS WITH THE VERDICT, so `agreed` can never be
        # read without knowing how much it was drawn from.
        "measured": sum(1 for f in fields.values() if f["measured"]),
        "of": len(fields),
        "fields": fields,
        "readings": graded,
    }


def _readable(flag: str, path: pathlib.Path) -> tuple[str | None, str]:
    """The file's text, or the fault named by the flag that asked for it.

    ! THE FLAG IS IN THE MESSAGE because the path alone does not say which
    argument carried it, and a run names up to four paths. A bare
    `FileNotFoundError` on a traceback leaves the caller matching a path against
    their own command line to work out which one they got wrong.
    """
    if not path.exists():
        return f"{flag}: no such file: {path}", ""
    if path.is_dir():
        return f"{flag}: is a directory, not a file: {path}", ""
    try:
        return None, path.read_text(encoding="utf-8")
    except OSError as e:
        return f"{flag}: cannot read {path}: {e.strerror or e}", ""


def inspect(args) -> tuple[list[str], str, dict]:
    """Every fault in the arguments, plus the two files that had to be read.

    !! CHECKED BEFORE ANY REQUEST IS MADE, WHICH IS THE WHOLE POINT. Each
    reading is a paid call, so a typo found after the calls has already cost
    money and thrown the readings away -- and a comparison is never written
    from a partial set (see `reread`). ! `--out` is included for the same
    reason: an unwritable destination discovered at the end loses everything.
    """
    problems: list[str] = []

    if args.runs < 2:
        problems.append(
            f"--runs={args.runs}: a comparison needs at least two readings."
        )

    # !! A CASE WITH NO END CANNOT EXERCISE THREE OF THE FIVE AXES, AND THE RUN
    # IS BILLED ANYWAY. MEASURED 2026-08-29: the first live T50 spent $0.61 and
    # returned `N/A` on detection, diagnosis and prescription in both readings,
    # so it bought one axis of stability at the price of five.
    #
    # ! REFUSED RATHER THAN WARNED, because a warning scrolls past and the money
    # is already gone by the time anyone reads the output. `--allow-no-end` is
    # the deliberate form -- T50 asks only whether the same input grades the
    # same way, so an unkeyed case IS legitimate for it, once chosen knowingly.
    if not args.allow_no_end and not (args.end and args.end_diff):
        missing = " and ".join(
            n for n, v in (("--end", args.end), ("--end-diff", args.end_diff)) if not v
        )
        problems.append(
            f"{missing}: without the answer key, {', '.join(KEYED_AXES)} all "
            f"grade N/A and the run still costs {COST_PER_READING} a reading. "
            "Supply the key, or pass --allow-no-end to measure the remaining "
            "axes deliberately."
        )

    fault, _ = _readable("--findings", args.findings)
    if fault:
        problems.append(fault)
    fault, _ = _readable("--under-review", args.under_review)
    if fault:
        problems.append(fault)

    diff = ""
    if args.end_diff:
        fault, diff = _readable("--end-diff", args.end_diff)
        if fault:
            problems.append(fault)

    mechanical: dict = {}
    if args.mechanical:
        fault, text = _readable("--mechanical", args.mechanical)
        if fault:
            problems.append(fault)
        else:
            try:
                loaded = json.loads(text)
            except json.JSONDecodeError as e:
                problems.append(
                    f"--mechanical: {args.mechanical} is not valid JSON "
                    f"(line {e.lineno}, column {e.colno}): {e.msg}"
                )
            else:
                # ! `to_grading_json` does `mechanical.get(...)`, so a list or a
                # bare number reaches it and fails with `AttributeError` after
                # the calls have been paid for.
                if isinstance(loaded, dict):
                    mechanical = loaded
                else:
                    problems.append(
                        f"--mechanical: {args.mechanical} holds a "
                        f"{type(loaded).__name__}, and a JSON object is required."
                    )

    if args.out.exists():
        problems.append(f"--out: {args.out} exists; a comparison is never overwritten.")
    else:
        try:
            args.out.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            problems.append(
                f"--out: cannot create {args.out.parent}: {e.strerror or e}"
            )

    return problems, diff, mechanical


def main(argv: list[str] | None = None) -> int:
    """The command T50 is run with, so the measurement is re-derivable."""
    parser = argparse.ArgumentParser(
        description="Grade one artifact N times with the same judge (T50).",
    )
    parser.add_argument(
        "--findings",
        type=pathlib.Path,
        required=True,
        help="the findings.md the run filed",
    )
    parser.add_argument(
        "--under-review",
        type=pathlib.Path,
        required=True,
        help="the file as it stood at START",
    )
    parser.add_argument("--start", required=True)
    # ! END IS OPTIONAL BECAUSE A CASE MAY NOT HAVE ONE. T50 only needs the same
    # input twice, and the rubric treats END as a POSITIVE key -- but C3/T51
    # calibrates against END and cannot run without it.
    parser.add_argument(
        "--end", default="", help="the answer-key commit; omit for a case with no END"
    )
    parser.add_argument(
        "--end-diff",
        type=pathlib.Path,
        help="file holding END's diff; omitted means none supplied",
    )
    parser.add_argument(
        "--mechanical",
        type=pathlib.Path,
        help="JSON file of the mechanical verification",
    )
    parser.add_argument("--arm", required=True)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument(
        "--allow-no-end",
        action="store_true",
        help="grade a case with no answer key, knowing three axes will be N/A",
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        required=True,
        help="where to write the comparison; must not exist",
    )
    args = parser.parse_args(argv)

    # ! A Windows console is cp1252 and this prints a path and the judge's
    # letters. `evals/` cannot import the shipped package's `utf8_console`, so
    # it spells the same three lines itself, as every script under `scripts/`
    # does. Gated by `tests/gates/test_shipped_cli_encoding.py`.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")

    problems, diff, mechanical = inspect(args)
    if problems:
        # !! EVERY FAULT AT ONCE, NOT THE FIRST. Reporting one per run makes a
        # three-flag mistake three edit-and-retry cycles, and the last two are
        # discovered only after the first is fixed.
        for problem in problems:
            print(f"REFUSED  {problem}", file=sys.stderr)
        return 1

    # ! BESIDE THE OUTPUT, NAMED AFTER IT. A run that dies partway leaves its
    # paid readings here, and a reader finds them without being told where.
    keep = args.out.parent / f"{args.out.stem}-readings"

    try:
        result = reread(
            findings=args.findings,
            under_review=args.under_review,
            start=args.start,
            end=args.end,
            end_diff=diff,
            mechanical=mechanical,
            arm=args.arm,
            eval_id=args.eval_id,
            runs=args.runs,
            # ! NO `--max-tokens` FLAG, DELIBERATELY. It is the model's ceiling
            # already, so the only thing a knob could do is lower it -- which is
            # exactly the bet that lost a run on 2026-08-29.
            keep=keep,
        )
    except grader.Spent as lost:
        # !! THE MONEY IS ALREADY GONE, AND SAYING SO IS THE POINT. This is not
        # a bad argument and not a setup problem: the request was billed and
        # returned nothing usable, so the caller needs to know what survived
        # before deciding whether to run it again.
        kept = sorted(keep.glob("reading-*.json")) if keep.exists() else []
        print(f"BILLED   {type(lost).__name__}: {lost}", file=sys.stderr)
        print(
            f"         {len(kept)} reading(s) already paid for were KEPT in {keep}"
            if kept
            else "         no reading completed, so nothing was kept.",
            file=sys.stderr,
        )
        return 3
    except grader.SetupProblem as refused:
        # ! A SEPARATE EXIT CODE, because it is the one failure that is neither
        # a bad argument nor a bad grade -- the machine is not set up, and a
        # caller may reasonably want to tell that apart. ! The BASE class is
        # caught: a missing credential and a missing workspace are both setup,
        # and catching only the first put a raw traceback in front of Roy on
        # the first live call this repo made.
        print(
            f"REFUSED  {type(refused).__name__}: {refused}",
            file=sys.stderr,
        )
        return 2
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    for field, seen in result["fields"].items():
        # ! `--` FOR AN UNMEASURED FIELD, never `==`. The two look alike at a
        # glance and mean opposite things: one is the judge agreeing, the other
        # is the judge having had nothing to grade.
        mark = "--" if not seen["measured"] else ("==" if seen["agreed"] else "!=")
        note = "  (not graded)" if not seen["measured"] else ""
        print(f"{field:<14} {mark}  {' '.join(seen['letters'])}{note}")
    print(
        f"\nagreed: {result['agreed']}  "
        f"over {result['measured']} of {result['of']} fields, "
        f"{result['runs']} readings"
    )
    if result["measured"] < result["of"]:
        print(
            f"! {result['of'] - result['measured']} field(s) were not graded, so "
            "this says nothing about them."
        )
    # ! WHAT IT SPENT, PRINTED. A run count is chosen by a human who is paying,
    # and the only honest input to that choice is what the last run actually
    # cost -- not an estimate written down once and left to rot.
    tokens = [r.get("usage") or {} for r in result["readings"]]
    into = sum(u.get("input_tokens") or 0 for u in tokens)
    out_of = sum(u.get("output_tokens") or 0 for u in tokens)
    if into or out_of:
        print(
            f"tokens: {into:,} in, {out_of:,} out over {result['runs']} readings"
            f"  ({out_of // max(result['runs'], 1):,} out per reading)"
        )
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
