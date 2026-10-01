#!/usr/bin/env python3
"""Convert agents/*.md (Claude Code subagents) to GitHub Copilot custom agents.

    python3 scripts/export-copilot.py [--out DIR] [--check]

Writes one `<name>.agent.md` per agent into DIR (default: ./.github/agents).
Copilot loads these in VS Code, on github.com, and in Copilot CLI.

What changes: the `tools:` list is mapped to Copilot tool aliases and the
`model:` line is dropped (Copilot uses the model picker). The prompt body is
copied verbatim, so the agents' rules stay identical on both platforms.

--check exits 1 if DIR is missing a file or has stale content (for CI).
Stdlib only; Python 3.8+. Copilot's agent schema evolves; verify against
GitHub's current custom-agents docs if a field is rejected.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Claude Code tool -> Copilot tool alias.
TOOL_MAP = {
    "Read": "read",
    "Write": "edit",
    "Edit": "edit",
    "Glob": "search",
    "Grep": "search",
    "Bash": "execute",
}

HEADER = (
    "<!-- Generated from agents/{src} by scripts/export-copilot.py. "
    "Edit the source, then re-run. -->\n"
)


def split_frontmatter(text, src):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{src}: no YAML frontmatter found")
    return m.group(1).split("\n"), m.group(2)


def convert(src_path):
    fm, body = split_frontmatter(src_path.read_text(encoding="utf-8"), src_path.name)
    out, tools = [], []
    for line in fm:
        if line.startswith("tools:"):
            names = [t.strip() for t in line[len("tools:"):].split(",") if t.strip()]
            for n in names:
                if n not in TOOL_MAP:
                    sys.exit(f"{src_path.name}: unmapped tool {n!r}; add it to TOOL_MAP")
                if TOOL_MAP[n] not in tools:
                    tools.append(TOOL_MAP[n])
        elif line.startswith("model:"):
            continue
        else:
            out.append(line)  # name, description (incl. folded continuation lines)
    if tools:
        out.append("tools: [" + ", ".join(f"'{t}'" for t in tools) + "]")
    return "---\n" + "\n".join(out) + "\n---\n" + HEADER.format(src=src_path.name) + body


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=".github/agents", help="output directory")
    ap.add_argument("--check", action="store_true", help="verify only; write nothing")
    args = ap.parse_args()

    out_dir = Path(args.out)
    stale = []
    sources = sorted((ROOT / "agents").glob("*.md"))
    if not sources:
        sys.exit("no agents/*.md found")
    for src in sources:
        dest = out_dir / f"{src.stem}.agent.md"
        content = convert(src)
        if args.check:
            if not dest.exists() or dest.read_text(encoding="utf-8") != content:
                stale.append(str(dest))
            continue
        out_dir.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        print(f"wrote {dest}")
    if args.check:
        if stale:
            print("out of date:\n  " + "\n  ".join(stale), file=sys.stderr)
            sys.exit(1)
        print("ok")


if __name__ == "__main__":
    main()
