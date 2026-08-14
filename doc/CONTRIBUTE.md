# Contributing to NormPic

This document is the canonical statement of how work is done in this
repository: how changes are planned, tested, committed, reviewed, and
documented.
It is the source of truth for these conventions.
Other documents (including doc/TODO.md) point here rather than
restating them, so the rules live in one place and do not drift.

## Security

This repository handles credentials for production infrastructure.
Never read shell environment variables.
Reading them risks leaking secrets into logs, command output, commits,
or generated files, and recovering from a leak means rotating live
credentials.
There is no contribution that requires reading the environment.

## Ways of working

Every change moves through the same path: plan, review, implement,
verify, submit.
Three roles participate, whoever fills them:

- Author: writes the plan, implements it, and reports a short summary
  after each commit.
- Reviewer: signs off the plan before any code is written, and runs
  quality assurance before the change is submitted.
- Maintainer: approves and performs the merge.

Plan-first is the rule.
No implementation begins before the plan is reviewed and signed off.
The plan is also the baseline that review grades against, so the
effort spent making it precise is repaid at review time.

## Planning

A change begins as a written plan: an ordered task list precise enough
that following it top to bottom produces the change and satisfies the
conventions in this document.

A well-formed plan has this shape:

- The first task is branching.
  `git checkout -b <prefix>/<slug>` from the current head, using one of
  the branch prefixes below.
- The body is a sequence of spec-then-test-then-implement cycles,
  grouped by behavior rather than by category.
  Each cycle names the spec it satisfies, the test that pins it, and
  the implementation that makes the test pass.
  Related cases for one rule stay in one cycle, because they verify a
  single boundary and a reviewer should see them together.
- Where a behavior has a known boundary or trap (an empty input, a
  leading-zero value, a null where a string is expected), the plan
  names the test that closes it.
  This is required wherever such a boundary exists,
  because a named boundary test is what allows to evaluate the plan &
  what review verifies directly.
- The plan cites the spec source each cycle satisfies
  (doc/architecture/manifest-contract.md,
  doc/architecture/conformance.md, schema/v0.1.0.json), so tests pin
  the documented contract and not an interpretation of it.
- The plan states scope concretely: which files change and roughly how
  much.
  A later diff that is disproportionate to this is a signal of drift.
- The final task is the documentation-and-planning update commit,
  described under Documentation discipline, leaving the change ready to
  submit.

When a planned change is recorded in doc/TODO.md, it takes the same
shape: a branch-named section, a short framing of the work, an ordered
task list that opens with the branch task, runs the cycles through the
middle, and closes with the documentation update.
A reader should be able to execute the section without reconstructing
the plan.

## Test-driven development

Test-driven development is the default discipline for any change that
alters behavior.

At the keyboard the rhythm is red, green, refactor: write a failing
test, make it pass, then improve the code with the test still green.
This is a working rhythm, not a commit boundary.
A single commit may contain several closely related cycles when they
form one coherent piece of work.

Build one behavior at a time, in small steps with clear logical breaks.
Run the relevant tests immediately after each testable addition.
Broken code is never committed: every commit leaves the suite green.

The conformance fixtures under test/fixture/conformance/ are a
language-agnostic artifact.
They are exercised through the Python suite today, but they are meant
to validate against schema/v0.1.0.json directly so that other
implementations can run them.
Do not bake Python-only assumptions into a fixture.

## Commits and branches

### The pre-commit quality gate

Before every commit, all applicable checks must pass.
For the Python code today, in this order:

1. `uv run ruff check`
2. `uv run pyright`
3. `uv run pytest` (the full suite, not a single file)

All three are enforced now; the tree is green under each.
When code in another language lands, that code's own checks join the
gate and must also pass.

`just check` runs these three in this order.
The list above is the definition; the recipe follows it, so a change
here requires the same change in the Justfile.

Use `uv run`, not a bare interpreter, or `just` which wraps it.
Run a focused file with `uv run pytest test/unit/test_name.py -v`
during development, but always run the full suite before committing.

### Commit sizing

Group commits by logical coherence.
A commit is a self-contained unit of related work that leaves the tree
green.

Sizes below are guidelines, not gates:

- A code commit around 300 lines is a soft ceiling.
  Going well past it usually means the work was divided badly, though
  not always.
  Staying under it is normal and is not a target to pad toward.
- Roughly two to eight commits per change.
  Added complexity can justify exceeding this.

A coherent, slightly larger unit is better than fragmenting one
behavior across many tiny commits or changes.

### Commit message format

- Title: at most 50 characters including the prefix.
- Title starts with a capital letter or a digit after the prefix and
  colon.
- Body: lines at most 72 characters, using "-" bullets with nested
  detail.
- No signature block: no emoji, links, or co-authored-by lines.

Commit prefixes:

- `Pln:` planning and TODO updates
- `Ft:` new feature or capability
- `Fix:` bug fix
- `Ref:` pure refactor, no new behavior
- `Doc:` documentation
- `Chr:` chore and maintenance
- `Tst:` test-only changes

### Branch names

Branches use a lowercase prefix, a slash, and a kebab-case slug:
`pln/`, `ft/`, `fix/`, `ref/`, `doc/`, `chr/`, `tst/`.
Examples: `ft/hash-blake2b-crockford`, `tst/conformance-harness`.
Refer to other work by branch name, never by an ordinal position,
which loses meaning when the sequence shifts.

## Quality assurance

Quality assurance is a gated, progressive hunt run before a change is
submitted.
It is a shared standard: the reviewer performs it, and the author
writes summaries and tests knowing how the work will be probed.

Its premise is that the green suite already proves mechanical
correctness, so review never re-derives that the code works.
Review spends its effort only on what tests cannot catch: a misread
spec, a missing but required thing, a false claim, and a latent trap.
It grades commits against the approved plan, starting from the author's
summary before reading the repository.

### The author's summary

After each commit the author reports: the subject, one sentence of what
changed, pass or fail, and a `git diff --stat`.
The stat is required, because scope drift is invisible in prose.
A one-line change that touched four hundred lines shows up only as a
number.

### The ladder

The checks run cheapest first.
Each rung runs only when its failure is possible for this change, which
is read for free from the plan and the summary.

- Summary against plan: does it describe doing what was approved?
  Watch for overclaims ("complete", "all", a specific count) and for
  scope beyond the plan.
- Scope, from the stat: only the expected files, and a size
  proportionate to the plan?
  A disproportionate diff is stopped and flagged before any content is
  read.
- Signatures, by targeted diff or grep rather than reading whole files:
  is the substantive change the one that was specified?
- Claims against ground truth, run only when the summary makes a
  falsifiable claim such as a count or an "all" or a "complete":
  verify it against the repository, not the prose.
- Completeness, run only when the change contributes to a defined set
  whose tests discover their members dynamically: a missing required
  member raises no failure, so check the set against its inventory.
- Trap reasoning, run only when the change touches correctness-bearing
  logic: the failure classes a passing suite does not exercise, such as
  vacuous conditions, boundary inputs, one defect producing many
  errors, and misattributed errors.

### The probe kit

A few load-bearing reads, around fifteen lines total, confirm that
tests assert what was intended.
Derive the targets from the plan, which names the new symbol, the
removed token, and the assertions it promised:

- Grep `assert` in the changed test files to read the assertions
  themselves, not just the test names.
  This catches an assertion that a good name hides but that verifies
  little.
- Grep the source for the removed or old token to confirm the migration
  is complete and any trap pattern is gone.
  Empty output is the proof.
- Grep test/ for the newly introduced symbol to confirm a test
  exercises it, rather than it being defined and never called.

Use `grep -I --include='*.py'` so compiled bytecode and other binaries
do not muddy the results.

These greps confirm the tests assert the right thing for the cases they
name.
Extending that confidence past the cases the author chose requires
independent ground truth, such as vectors computed by a separate tool,
not the implementation under test.

### Deleting a rung

The strongest check is one that no longer needs a reviewer.
When a failure mode recurs, push it into a suite assertion so it goes
red on its own instead of costing a review pass.
For example, asserting that a fixture count equals its inventory count
means a skipped member can never again pass silently.

### The reviewer's own analysis is not exempt

The same standard the reviewer applies to the author's claims
applies to the reviewer's own reasoning.
A hazard the reviewer infers (a determinism risk, a missing
dependency, a contract collision) is a claim, not a finding, until
it is checked against the code or the contract document.
Do not escalate an inferred hazard to the maintainer as a decision
before reading the source that would confirm or dismiss it.
If the spec or the code already answers a question, read it; do not
ask the maintainer.
The maintainer's time is spent only on genuine direction calls, not
on questions the repository already answers.

When the reviewer is wrong, the correction is stated plainly once
("that was wrong; it is X") and the analysis moves on.
A corrected position is not restated as though it were the original
position, and the same fact is not re-explained in varying forms;
both make a session impossible to track.

### Sign-off

A change is signed off when its commits match the plan, its scope is
contained, every claim checks against ground truth, and the applicable
trap and completeness rungs found nothing.
Open items go back as specific, surgical requests, not as a direction
to start over.

## Coordinating work across roles

The reviewer role is often a coordinator: a conduit between an author
(who may be a separate person or model instance) and the review
standard in this document.
The author writes plans and implements; the coordinator grades against
the plan, runs QA, and relays sign-offs and surgical change requests;
the maintainer merges.

### Relay mechanics

- The author reports plans and per-commit summaries; the coordinator
  reviews against the repository, never against the prose alone.
- Shell output moves by clipboard relay: the maintainer runs commands
  and pastes results back, so coordinator requests should be targeted
  (specific greps and line ranges), not "send me the whole file".
- When a commit is ready, the coordinator provides the shell commands
  and the commit message as separate blocks, so the message can be
  pasted without being embedded in a command.
- The coordinator writes commit messages; the author does not.

### Per-commit sign-off on fragile changes

Most PRs are signed off as a unit.
A dependency-ordered PR whose commits are preconditions for one
another (a schema cutover, a field removal that spans model,
serializer, and tests) is signed off per commit: plan the one commit,
sign off, implement, summarize, sign off, commit, then the next.
This prevents an out-of-order change that breaks an intermediate tree.
Where such an ordering exists, encode it in the TODO section for that
PR, with the reason each step precedes the next.

### The manual acceptance run

The green suite proves mechanical correctness on fixtures; it does not
prove the program behaves on real data.
For changes that touch the end-to-end path, the coordinator runs the
actual program on a real collection before the final sign-off, and
checks what fixtures cannot: no dangling symlinks, output validates
against the canonical schema, no removed fields present, files open
through the produced links.
This pattern has caught producer-side drift that every fixture test
passed.

### Communication norms

- Terse and direct; one topic at a time.
- A single concrete recommendation, not a menu of options.
- State a correction once and move on; do not restate a settled call.
- Recalibrate immediately when the maintainer flags drift, without
  re-litigating.

## Style and formatting

These rules apply to all text in the repository: code, comments,
docstrings, commit messages, and pull request descriptions.

- ASCII only.
  No em dashes, no emoji, no decorative Unicode.
  A rare document may justify an exception, called out explicitly when
  it arises.
- Line length depends on context:
  - Commit body lines at most 72 characters (enforced).
  - Prose and documentation lines at most 80 characters.
  - Python code lines at most 88 characters (ruff default).
- In prose, sentence-ending punctuation is followed by a newline.
  A sentence longer than the prose limit breaks at a natural point
  before the limit.
- Singular directory and field names by default: `doc/` not `docs/`,
  `test/` not `tests/`, `asset/` not `assets/`.

Code conventions:

- Functions carry a docstring.
- Code is type annotated; prefer dataclasses for basic data structures.
- Match the patterns and formatting of neighboring files.
- Verify a library is available before using it.
- Follow PEP 8 and ruff: no trailing whitespace, a blank line at end of
  file, two blank lines between top-level definitions, one between
  methods, spaces around operators and after commas.

## Documentation discipline

### Single source of truth

A fact lives in exactly one place.
The manifest's fields, semantics, and canonical forms live in
doc/architecture/manifest-contract.md.
Conformance rules live in doc/architecture/conformance.md.
The machine-readable schema is schema/v0.1.0.json.
Do not restate these in other documents.
Point to them, so they cannot drift out of agreement.

### Documentation hierarchy

Every document is reachable from the root README through a chain of
links.
The top-level README gives the overview and links into doc/README.md.
Each directory has a README acting as its index.
A document links to peers at its own level or to a subdirectory README
one level down, never deeper.
No document is an orphan.

### Maintaining state during a change

doc/TODO.md and doc/CHANGELOG.md are maintained throughout, treated as
append-and-prune.
Do not read either file end to end to make an edit.
Find the section with `grep -n`, view a few lines around it, and edit
surgically.

After each commit, append one concise line to doc/CHANGELOG.md under
today's date header, and mark the corresponding doc/TODO.md item done
in place without deleting it yet.

The final commit of a change consolidates the per-commit CHANGELOG
lines under today's date into one summary block, deletes the granular
lines, removes the now-complete task lines from doc/TODO.md, and updates
any reference document the change affected.
