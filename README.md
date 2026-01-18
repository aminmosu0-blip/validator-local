# Validator Local (Milestone A)

Validator Local is a hermetic, explainable validation runner for platform-style coding problems.
It validates a submission folder containing:

- repo.zip (target repository)
- Dockerfile.problem
- test.patch
- solution.patch
- description.txt

Primary goal: deterministic, offline-friendly validation with reproducible outputs.

## Folder workflow

Create a folder with:
- repo.zip (or exactly one *.zip)
- Dockerfile.problem
- test.patch
- solution.patch
- description.txt
- validator.toml (optional)

Example:
  submissions/job1/
    repo.zip
    Dockerfile.problem
    test.patch
    solution.patch
    description.txt
    validator.toml

Run triad:
  validator triad --dir /absolute/path/to/submissions/job1

Static/preflight only:
  validator static --dir /absolute/path/to/submissions/job1

## Outputs

Each run writes to:
  <dir>/.validator_runs/<job_id>/

Includes:
- report.json              canonical structured report
- triad_summary.json       one-line triad verdict and timings
- stage_logs/*.log         docker build, pytest runs, patch apply logs
- bundle.zip               portable repro bundle (inputs + logs + metadata)

bundle.zip is designed to reproduce failures elsewhere.

## Triad contract

1) Apply only test.patch:
   - base must pass
   - new must fail

2) Apply test.patch + solution.patch:
   - base must pass
   - new must pass

## Policy configuration (validator.toml)

Example:

  [limits]
  docker_build_timeout_s = 900
  base_timeout_s = 900
  new_timeout_s = 900
  postchecks_timeout_s = 300
  max_log_bytes = 2000000

  [docker]
  network = "none"
  cpus = 2.0
  memory = "4g"

  [gates]
  test_patch_min_bytes = 14336
  solution_patch_min_bytes = 2765
  description_ascii_only = true
  description_lf_only = true

  [rules.patch_boundaries]
  enforce_test_patch_boundaries = true
  enforce_solution_patch_boundaries = true

  [rules.test_sh]
  enforce_base_ignores_new = true
  enforce_new_runs_only_new = true
  forbid_backticks = true

Policy is checked before any expensive work.

## API mode

Start:
  python -m uvicorn app:app --host 127.0.0.1 --port 8000

Validate folder:
  POST /v1/jobs/from-dir?wait=true
  {"dir_path":"/absolute/path/to/submissions/job1"}

## Roadmap

Milestone A (done here):
- policy, preflight gates, timeouts/resource limits, triad runner, bundles, structured reports.

Next:
- JUnit and SARIF exports, job history index, stricter sandboxing, runner queue.
