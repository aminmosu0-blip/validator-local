import argparse
import json
import sys
from pathlib import Path

from validator.api import run_static_from_dir, run_triad_from_dir

def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="validator", description="Folder-first validator (triad + preflight + bundles).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_static = sub.add_parser("static", help="Run preflight/static checks only.")
    p_static.add_argument("--dir", required=True, help="Folder containing repo.zip + artifacts.")

    p_triad = sub.add_parser("triad", help="Run full triad (test-only then test+solution).")
    p_triad.add_argument("--dir", required=True, help="Folder containing repo.zip + artifacts.")

    args = parser.parse_args(argv)

    dir_path = str(Path(args.dir).resolve())

    if args.cmd == "static":
        res = run_static_from_dir(dir_path)
        _print_json(res)
        return 0 if res.get("ok") else 1

    if args.cmd == "triad":
        res = run_triad_from_dir(dir_path)
        _print_json(res)
        return 0 if res.get("ok") else 1

    return 2

if __name__ == "__main__":
    raise SystemExit(main())
