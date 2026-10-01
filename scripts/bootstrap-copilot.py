#!/usr/bin/env python3
"""Set up the design-docs pipeline for GitHub Copilot in an existing project.

    python3 scripts/bootstrap-copilot.py PROJECT_DIR [--vendor MODE] [--docs-dir DIR]

Run it from a clone of this repo. It:
  1. vendors this repo into PROJECT_DIR/design-docs-template/ (see --vendor),
  2. generates PROJECT_DIR/.github/agents/*.agent.md (scripts/export-copilot.py),
  3. adds a design-docs block to PROJECT_DIR/.github/copilot-instructions.md,
     creating the file if needed. The block sits between marker comments, so
     re-running replaces it in place and never touches the rest of the file,
  4. creates PROJECT_DIR/<docs-dir>/ for the working documents.

--vendor copy       copy the template (no git history, no SampleDocs). Default.
--vendor submodule  `git submodule add` from this clone's origin URL; PROJECT_DIR
                    must be a git repo.
--vendor none       the template is already at PROJECT_DIR/design-docs-template.

If PROJECT_DIR/design-docs-template already exists, vendoring is skipped. Safe
to re-run. Stdlib only; Python 3.8+.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = "design-docs-template"
BEGIN = "<!-- design-docs:begin (managed by bootstrap-copilot.py; edits inside are overwritten) -->"
END = "<!-- design-docs:end -->"
COPY_IGNORE = shutil.ignore_patterns(".git", "SampleDocs", "__pycache__", "*.pyc")


def vendor(project, mode):
    dest = project / TEMPLATE_DIR
    if mode == "none":
        if not dest.is_dir():
            sys.exit(f"--vendor none, but {dest} does not exist")
        return
    if dest.exists():
        print(f"skip vendoring: {dest} already exists")
        return
    if mode == "copy":
        shutil.copytree(ROOT, dest, ignore=COPY_IGNORE)
        print(f"copied template -> {dest}")
        return
    url = subprocess.run(
        ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
        capture_output=True, text=True,
    ).stdout.strip()
    if not url:
        sys.exit("--vendor submodule needs this clone to have an 'origin' remote")
    subprocess.run(
        ["git", "-C", str(project), "submodule", "add", url, TEMPLATE_DIR], check=True
    )


def update_instructions(project, docs_dir):
    snippet = (ROOT / "templates" / "COPILOT_INSTRUCTIONS.snippet.md").read_text(encoding="utf-8")
    snippet = snippet.replace("{{DOCS_DIR}}", docs_dir).replace("{{TEMPLATE_DIR}}", TEMPLATE_DIR)
    block = f"{BEGIN}\n{snippet.rstrip()}\n{END}\n"
    path = project / ".github" / "copilot-instructions.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if BEGIN in old and END in old:
        head, rest = old.split(BEGIN, 1)
        tail = rest.split(END, 1)[1].lstrip("\n")
        new = head + block + (("\n" + tail) if tail else "")
    else:
        new = (old.rstrip() + "\n\n" if old.strip() else "") + block
    path.write_text(new, encoding="utf-8")
    print(f"updated {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("project", help="path to the existing project")
    ap.add_argument("--vendor", choices=["copy", "submodule", "none"], default="copy")
    ap.add_argument("--docs-dir", default="docs/design",
                    help="project-relative folder for the working documents")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not project.is_dir():
        sys.exit(f"{project} is not a directory")
    if project == ROOT:
        sys.exit("PROJECT_DIR is this template repo; point it at your own project")

    vendor(project, args.vendor)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export-copilot.py"),
         "--out", str(project / ".github" / "agents")],
        check=True,
    )
    update_instructions(project, args.docs_dir.strip("/"))
    (project / args.docs_dir).mkdir(parents=True, exist_ok=True)
    print(f"\nDone. Commit .github/, {TEMPLATE_DIR}/ and {args.docs_dir}/, then pick an agent "
          "in Copilot Chat and give it your brief.")


if __name__ == "__main__":
    main()
