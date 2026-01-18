# Agent Workflow (Platform-style Python Problem Authoring)

This repo provides a validator that enforces a platform-style problem workflow:
- deterministic/offline
- strict patch boundaries
- triad contract (base/new gating)
- size gates without padding

## Expected submission folder
- repo.zip
- Dockerfile.problem
- test.patch
- solution.patch
- description.txt

## Patch boundaries
- test.patch may change only:
  - test.sh
  - exactly one tests/test_*_problem.py
- solution.patch must modify production code only (no tests/scripts/Dockerfile)

## test.sh rules
- must support: ./test.sh base and ./test.sh new
- base ignores new test file
- new runs only the new test file
- no piping to tail; do not hide failures
- forbid backticks

## Triad contract
- test.patch only: base pass, new fail
- test.patch + solution.patch: base pass, new pass

## Size gates
Default policy:
- test.patch >= 14 KiB
- solution.patch >= 2.7 KiB
Do not pad. Expand only via real invariants/entrypoints.

## Determinism
Validator sets:
- PYTHONHASHSEED=0
- TZ=UTC
- LC_ALL=C
and supports docker network=none.

## Output and reproducibility
Every run produces:
- report.json
- triad_summary.json
- bundle.zip (inputs + logs + metadata)

bundle.zip should allow reproducing any failure on another machine.
