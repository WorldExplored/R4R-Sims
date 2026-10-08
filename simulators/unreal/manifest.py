#!/usr/bin/env python3
"""Create a source manifest or verify a copied run against that manifest."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def create(directory):
    entries = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name != "source-manifest.json":
            entries.append({"path": path.relative_to(directory).as_posix(),
                            "bytes": path.stat().st_size, "sha256": digest(path)})
    output = {"schema": 1, "source_run": directory.name, "files": entries}
    (directory / "source-manifest.json").write_text(json.dumps(output, indent=2) + "\n")
    print(f"source manifest: {len(entries)} files, {sum(e['bytes'] for e in entries)} bytes")


def verify(directory):
    manifest = json.loads((directory / "source-manifest.json").read_text())
    errors = []
    expected = {entry["path"] for entry in manifest["files"]}
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*")
              if p.is_file() and p.name != "source-manifest.json"}
    for extra in sorted(actual - expected):
        errors.append(f"unlisted file: {extra}")
    for entry in manifest["files"]:
        path = directory / entry["path"]
        if not path.is_file():
            errors.append(f"missing: {entry['path']}")
        elif path.stat().st_size != entry["bytes"] or digest(path) != entry["sha256"]:
            errors.append(f"mismatch: {entry['path']}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"verified against source manifest: {len(expected)} files")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("create", "verify"))
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    directory = args.run_dir.resolve()
    if args.mode == "create":
        create(directory)
    else:
        verify(directory)


if __name__ == "__main__":
    main()
