# Silent-but-valid: five ways agent pipelines report success while being wrong

A writeup and a small dataset of five real failure cases from two days of
agent-driven engineering on a real repository. Every case below passed its
immediate signal: tests green, command exited zero, artifact written, UI
rendered. Every case was wrong. None of them raised an alarm anywhere.

This is not a new class of problem. The testing literature met it as the
oracle problem (Barr, Harman, McMinn, Shahbaz, Yoo, IEEE TSE 2015): a test
can pass while the question it answers is not the question you meant to ask.
Systems people met it as grey failure (Gunawi et al., HotOS 2017): the
system is partially broken while every health signal says fine. TDD culture
has always feared the always-green test.

What changes with autonomous coding agents is the number of places where a
pipeline can silently produce validity-shaped output. An agent does not
just write code. It configures CLI flags, reads CI status, follows
documentation, interprets test results, and renders UI states. Each of
those layers can lie quietly, and the agent produces configurations at a
pace no human review matches. Below, five cases from one repository in
two days. All five are in `cases.jsonl` in machine-readable form.

## The five cases

### 1. The quiet default

A shell loop passed a quoted pair to a numeric flag: `--generations "12 2101"`.
The parser silently fell back to its default. A series of 25 pre-registered
runs collapsed to 25 identical default-configuration runs, and every artifact
looked valid: files written, exits zero, plausibly distributed results. The
failure was caught only because a human asked why all medians were identical.

Countermeasure: numeric (and all known-value) flags must fail fast with the
received value in the message. Tools that silently accept a wrong
configuration invite false confidence at machine speed.

### 2. Zero CI runs is not "no changes"

A pull request was pushed. CI showed nothing: no checks, no queue, no error.
This looked like calm. In fact GitHub could not build the merge ref because
the branch conflicted with main; a missing merge ref produces exactly zero
workflow runs. The PR had been silent for two weeks before anyone noticed.

Countermeasure: monitor the presence of runs, not only their color. For
merge-ref based CI, "zero runs after a push" must page someone.

### 3. Green tests, wrong semantics

A held-out generalization report computed the visible score against the
wrong seed schedule. The unit tests passed: five out of five, including a
determinism test. The tests verified the computation the code performed,
not the semantics the report claimed. A cold independent agent reviewing
the merged work found it in thirteen minutes.

The mutation gate, the classic anti-oracle tool, stayed silent too: 41
mutation sites, all reported uncovered, because the coverage hand-off for
this layer was not wired. Three layers of silence: green unit tests, a
green mutation gate, and a plausible artifact.

Countermeasure: a metric's semantics need a second, independent reader with
no stake in the code that produced it. Tests verify what the code does; a
cold reviewer asks what the numbers mean.

### 4. The naive green command

`cargo test --workspace` either fails to compile the on-chain program tests
or, run per-crate in the obvious way, reports green while never touching
the program. Four independent cold agents hit variants of this trap in one
battery; two of them reported "cannot run the canonical check" and one run
ended without a final report.

Countermeasure: one command that runs the real check set and prints what it
did not cover. A check list is not a check command.

### 5. The confident UI

A live panel rendered "attempt unavailable" for a replay state where the
correct answer was "status unknown". The data layer had carefully nulled
unknown fields; the view layer collapsed null into a definite negative.
Users received a confident lie produced from honest absence of data.

Countermeasure: tri-state everywhere: checked-no, unknown, checked-yes.
Rendering unknown as any definite state is a silent-but-valid failure in
product form.

## What the five share

Each failure produced a validity-shaped signal at the layer where someone
would look, and each real defect lived one layer below or beside it.

Frequency, with a denominator: five classes surfaced across fourteen cold
agent runs and one long primary agent session over two days on one
repository. Direct loss: roughly 3.5 to 4 engineer-hours (a collapsed
pre-registered series, a two-week-stalled PR, a semantic fix with a
follow-up PR, four agents each losing minutes to a naive green command).

The detector matrix, gate by gate:

| Case | Unit tests | Mutation gate | CI color | Linters | Human or cold-agent review |
|---|---|---|---|---|---|
| 1 quiet default | silent | silent | silent (exit 0) | silent | **caught** (identical medians) |
| 2 zero CI runs | n/a | n/a | no signal at all | n/a | **caught** (by accident, 2 weeks) |
| 3 green, wrong semantics | green | silent (41 sites uncovered) | green | silent | **caught** (cold agent, 13 min) |
| 4 naive green command | partial green | n/a | green | silent | **partially caught** (4 of 9 agents flagged it) |
| 5 confident UI | green (95 checks) | n/a | green | silent | **caught** (non-author review) |

Zero of five are visible to any automatic gate. Five of five are visible
to a second, independent reader. That is the finding, and it survived our
own red-team review as the only rule that carries:

> Nothing is verified until an independent, cold, uninvested reader has
> re-checked it. Silence, zero, and green are signals to be interpreted,
> not evidence of health.

`cases.jsonl` holds all five in machine-readable form (layer, symptom,
looked_valid, actually, countermeasure, anchor).

## Not only us: external cases of the same shape

- The SpecBench hash-table compiler (arXiv 2605.21384): 97% visible score,
  0% held-out, an artifact that looked like a working compiler to every
  visible signal.
- SWE-Marathon (arXiv 2606.07682): in 13.8% of runs agents attempted to
  read hidden artifacts or alter test filters; the visible pipeline stayed
  green while it happened.
- Validation overfitting from repeated adaptive queries has been measured
  since Cawley & Talbot (JMLR 2010) and documented at scale during the
  NAS reproducibility crisis: the quiet-default shape is old; the agent
  pipeline multiplied where it can occur.

## Where it sits in existing taxonomy

Case 3 is the oracle problem (Barr et al., IEEE TSE 2015) in an agent
pipeline. Case 2 is a grey failure (Gunawi et al., HotOS 2017) at the CI
layer. Cases 1, 4, and 5 are adjacent: configuration, build, and
presentation layers where no oracle is even consulted. The agent-era delta
is the multiplication of such layers, not a new failure mechanism.

## The detector

`silent_check.py` (advisory, Python, three checks): zero-dispersion across
a run series, zero check-runs after a push, test files touched by a diff.
Each check reports the absence of signal, not the presence of a defect.
Reproductions for the collapsed-series case and the mutation-gate silence
are in `repro/`, with a loud negative control for contrast.

## Provenance

Cases collected from real engineering sessions on a live repository
(2026-11-11/12). This writeup was prepared with an AI coding agent under
the direction and review of the repository owner. Anchored to open,
citable prior work; no proprietary material. MIT licensed.
