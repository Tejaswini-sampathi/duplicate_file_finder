
"""Duplicate File Finder and Organizer with student extensions."""

import csv
import filecmp
import hashlib
import shutil
from pathlib import Path

from common import Store, form, heading, note, table, run


store = Store(
    Path(__file__).with_name("data.json"),
    {"plan": [], "findings": [], "created": []},
)

CSV_FILE = Path(__file__).with_name("duplicate_findings.csv")


def scan(folder, extensions="", min_size=0):
    root = Path(folder).expanduser().resolve()

    if not root.is_dir():
        raise ValueError("Enter an existing folder path.")

    try:
        min_size = int(min_size or 0)
    except (TypeError, ValueError):
        raise ValueError("Minimum file size must be a number in bytes.")

    if min_size < 0:
        raise ValueError("Minimum file size cannot be negative.")

    # Accept extensions like pdf, .jpg, txt
    allowed_extensions = {
        ext.strip().lower()
        if ext.strip().startswith(".")
        else "." + ext.strip().lower()
        for ext in extensions.split(",")
        if ext.strip()
    }

    groups = {}
    files = []

    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue

        # Ignore files created by this app.
        if "_organized" in path.relative_to(root).parts:
            continue

        if path.resolve() == CSV_FILE.resolve():
            continue

        if allowed_extensions and path.suffix.lower() not in allowed_extensions:
            continue

        if path.stat().st_size < min_size:
            continue

        digest = hashlib.sha256()

        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)

        key = (path.stat().st_size, digest.hexdigest())
        groups.setdefault(key, []).append(path)
        files.append(path)

    duplicates = []

    for (size, _), paths in groups.items():
        if len(paths) > 1:
            equal = [
                path for path in paths
                if filecmp.cmp(paths[0], path, shallow=False)
            ]

            if len(equal) > 1:
                duplicates.append((size, equal))

    return root, files, duplicates


def build_plan(root, files):
    plan = []

    for index, source in enumerate(files, 1):
        category = source.suffix.lower().lstrip(".") or "no_extension"
        target = (
            root / "_organized" / category
            / f"{index}_{source.name}"
        )

        plan.append([str(source), str(target)])

    return plan


def build_findings(duplicates):
    findings = []

    for group_number, (size, paths) in enumerate(duplicates, 1):
        for path in paths:
            findings.append([
                group_number,
                path.name,
                str(path),
                size,
            ])

    return findings


def export_findings():
    findings = store.data.get("findings", [])

    if not findings:
        raise ValueError("No duplicate findings to export. Scan a folder first.")

    with CSV_FILE.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "Group Number",
            "File Name",
            "File Path",
            "Size (Bytes)",
        ])
        writer.writerows(findings)

    return note(f"CSV export completed: {CSV_FILE}")


def view():
    out = note(
        "Scan a folder to find duplicate files. "
        "Original files are retained."
    )

    out += form(
        "scan",
        [
            ("folder", "Full folder path", "text", ""),
            ("extensions", "File extensions (comma-separated; blank = all)", "text", ""),
            ("min_size", "Minimum file size in bytes (0 = all)", "number", "0"),
        ],
        "Scan and preview",
    )

    out += heading("Duplicate Groups")
    out += table(
        ["Group", "File Name", "File Path", "Size (Bytes)"],
        store.data.get("findings", []),
    )

    out += heading("Organization Preview")
    out += table(
        ["Original", "Proposed Copy"],
        store.data.get("plan", []),
    )

    out += form("export", [], "Export Findings as CSV")
    out += form("copy", [], "Create Organized Copies")
    out += form("undo", [], "Undo Last Copy Operation")

    return out


def handle(data):
    action = data["action"]

    if action == "scan":
        if store.data.get("created"):
            raise ValueError(
                "Undo the previous copy before preparing another plan."
            )

        root, files, duplicates = scan(
            data["folder"],
            data.get("extensions", ""),
            data.get("min_size", 0),
        )

        store.data["plan"] = build_plan(root, files)
        store.data["findings"] = build_findings(duplicates)
        store.save()

        waste = sum(
            size * (len(paths) - 1)
            for size, paths in duplicates
        )

        result = heading("Duplicate Scan Results")
        result += note(f"Found {len(duplicates)} duplicate group(s).")
        result += note(
            f"Estimated redundant storage: {waste} bytes."
        )
        result += table(
            ["Group", "File Name", "File Path", "Size (Bytes)"],
            store.data["findings"],
        )

        if not duplicates:
            result += note("No duplicate files matched these filters.")

        return result

    if action == "export":
        return export_findings()

    if action == "copy":
        if not store.data.get("plan") or store.data.get("created"):
            raise ValueError(
                "Prepare a new preview first, or undo the last copy."
            )

        # Validate all sources and destinations before copying.
        for source, target in store.data["plan"]:
            if not Path(source).is_file() or Path(target).exists():
                raise ValueError(
                    "A source is missing or a destination already exists. "
                    "Scan again."
                )

        store.data["created"] = []
        store.save()

        try:
            for source, target in store.data["plan"]:
                destination = Path(target)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

                fingerprint = hashlib.sha256(
                    destination.read_bytes()
                ).hexdigest()

                store.data["created"].append({
                    "path": str(destination),
                    "hash": fingerprint,
                })
                store.save()

        except Exception:
            # Keep a record of successfully created copies for safe undo.
            store.save()
            raise

        return note(
            "Organized copies created. Original files have not been changed."
        )

    if action == "undo":
        created = store.data.get("created", [])

        # Check every copy before removing any of them.
        for entry in created:
            target = Path(entry["path"])

            if (
                target.exists()
                and hashlib.sha256(target.read_bytes()).hexdigest()
                != entry["hash"]
            ):
                raise ValueError(
                    "A copied file was edited. Move it elsewhere before undoing."
                )

        for entry in created:
            Path(entry["path"]).unlink(missing_ok=True)

        store.data["created"] = []
        store.data["plan"] = []
        store.save()

        return note("Copies removed. Empty category folders may remain.")

    raise ValueError("Unknown action.")


if __name__ == "__main__":
    run("Duplicate File Finder and Organizer", view, handle)
