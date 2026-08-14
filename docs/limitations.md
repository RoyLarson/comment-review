# Limitations

## Notes for Changes

**Every example here is invented. Keep it that way.** A real quotation teaches a reviewer to
recognise *that comment* instead of the shape, and it rots — a hygiene skill carrying its own
obituary. Measurements anonymise for free.

⚠⚠ **THE BUDGET IS THE POINT, AND IT IS PER FILE.** A tight budget forces a *generalization*
instead of one rule per incident; without it these files become a case file for whatever repo
they last ran in — fitted to that project, useless to the next. **This is the opposite of the
cap rule for comments**, and the reason is what is optimised: **a comment must be true about
ONE thing, so cutting to fit deletes its evidence; a rule must cover MANY, so cutting to fit
forces the covering abstraction.**

Three questions before adding anything. Would it fire in a repo about something else? Is the
evidence a **number or ratio** rather than a story? Does it change what a reviewer **does**?
Assume a reasoning reader: state the rule and its discriminator, not the argument for it. At
budget, a new rule **replaces** one — and if two rules are instances of one generalization,
write the generalization and delete both.

⚠ **A rule belongs in exactly one file.** Shared contract → `reviewer-brief.md`; one angle's →
that angle's agent definition; apply-side → `sweep.md`; orchestration → here. Restating one
across two files is the antipattern this skill exists to find, and the four agents are the
place it will happen — they read alike and invite copy-paste.

**Any Python shipped here must be generic** — no hardcoded paths, no assumed directory names,
no cap baked into a script whose prose says the skill has no cap of its own.