# Repro 2: zero CI runs looks like calm

Live, public example (read-only, no setup):

    gh api "repos/unclebob/Acceptance-Pipeline-Specification/actions/runs?branch=review/security-deps-20261027" \
      --jq '.workflow_runs[0].created_at'

Before the branch was rebased on 2026-11-11, pushes to it produced zero
workflow runs for days: GitHub could not build the merge ref (conflict with
main), and a missing merge ref means no runs, no queue, no error. The two
October runs visible in history are from before the conflict appeared.

To reproduce on your own repo: push a branch that conflicts with the base,
then watch the Actions tab stay empty. Detector: silent_check.py runs.
