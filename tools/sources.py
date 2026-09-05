"""Check the Git submodule commits recorded in sources.lock.json."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "sources.lock.json").read_text())


def git(path, *args, capture=False):
  return subprocess.run(
    ["git", "-C", str(path), *args], check=True, text=True,
    stdout=subprocess.PIPE if capture else None,
  )


def check_checkout(repo):
  path = ROOT / repo["path"]
  if not (path / ".git").exists():
    raise RuntimeError(f"Uninitialized source: {repo['path']}; run bootstrap")
  head = git(path, "rev-parse", "HEAD", capture=True).stdout.strip()
  if head != repo["commit"]:
    raise RuntimeError(f"Unexpected checkout at {repo['path']}: {head}")
  changes = git(path, "status", "--porcelain", "--untracked-files=normal",
                capture=True).stdout
  if changes:
    raise RuntimeError(f"Local changes in {repo['path']}; preserve them before continuing")
  parent = ROOT / "omarchy" if repo["name"] == "packages" else ROOT
  name = "ports/k3/packages" if repo["name"] == "packages" else repo["path"]
  entry = git(parent, "ls-files", "--stage", "--", name, capture=True).stdout.split()
  if len(entry) < 4 or entry[0] != "160000" or entry[1] != repo["commit"]:
    raise RuntimeError(f"Manifest and submodule pin disagree: {repo['name']}")
  print(f"PIN_OK {repo['name']} {head}", flush=True)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("action", choices=["bootstrap", "verify"])
  parser.add_argument("--without-kernel", action="store_true",
                      help="Skip the large kernel checkout; kernel builds still need it")
  args = parser.parse_args()
  if args.action == "bootstrap":
    paths = ["omarchy", "noVNC"] if args.without_kernel else ["omarchy", "kernel", "noVNC"]
    git(ROOT, "submodule", "update", "--init", "--recursive", "--depth=1", "--", *paths)
  for repo in LOCK["repositories"]:
    if args.without_kernel and repo["name"] == "kernel":
      print("SKIPPED kernel (explicit --without-kernel)", flush=True)
      continue
    check_checkout(repo)
  print("Source pins verified. Arch dependency repositories remain rolling.")


if __name__ == "__main__":
  try:
    main()
  except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
    print(f"Source setup failed: {error}", file=sys.stderr)
    sys.exit(1)
