# census.py walks the whole repo, runs git twice, and its run-flush never fires

```
Status:   open
Progress: 0 of 7 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-22 (/simplify rounds 1 and 2 and /code-review high round 3,
          2026-08-22; round 2 measured the walk at 53% of a run)
```

## Objective

census.py walks the whole repo, runs git twice, and its run-flush never fires.

## Tasks

- [ ] MEASURED 2026-08-22: code_names walks and resolves the WHOLE tree to harvest
      60 files -- 53% of a census run. 3,152 paths walked, 3,021 of them in
      corpora/, 66 tracked -- and resolve() runs BEFORE the tracked test. When
      tracked is not None the answer is already in hand as repo-relative strings.
      ! corpora/ is only partly fetched here; after fetch_corpora.py the first row
      becomes tens of thousands of paths rglobbed and resolved PER RUN
- [ ] git ls-files is spawned TWICE per run (census.py:301-302), two full index
      dumps for one answer
- [ ] census.py:501 -- flush_run() never fires on a b.path change and BOTH
      continues bypass it. VERIFIED: constants.py, 43 lines, carries a row reading
      15-72 @c2..b58 41-0 -- another file intervals attributed to it, a NEGATIVE
      span, and any add composed from that row cites an address that does not
      exist
- [ ] CENSUS LOADING IS WRITTEN FOUR TIMES AND THE FOURTH DIVERGES.
      verdicts.py:335 never unwraps the dict form the other three accept
      (addresser.py, galley.py, record.py). ! Round 2 checked and NOTHING in the
      tree or the tests emits that dict form -- so three modules carry dead
      defensive code and the fourth is inconsistent with them. addresser already
      owns unaddressed() and is the vacant home for a load_census
- [ ] census._report is 289 lines, with --languages wrapped in redirect_stdout for
      no reason
- [ ] referrers.py:53 re-spells the (.py, .pyi) suffix tuple that language.py:99
      already owns -- the same defect as tier-dispatched-on-name, in a fourth
      place
- [ ] referrers.py:128 SPAWNS ONE git grep PER TOKEN -- about 200 subprocesses for
      a 17-file review, each one a full tree scan. MEASURED 2026-08-22: 37 tokens
      took 2.288s one at a time against 0.074s batched, a 31x difference. git grep
      takes repeated -e, and -o preserves the per-token attribution the report
      prints. ! Filed here on Roy ruling 2026-08-22 -- referrers supports the
      whole thing and is not part of the front half that will shift
