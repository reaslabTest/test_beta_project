---
name: workspace-conventions
description: Conventions for tools, skills, and project state in ReasLab workspaces.
---

## Tools

Standard shell tools are available in PATH. Use them directly.

- Build Lean projects: `lake build`, `lake build Mathlib.Order.Basic`
- Compile LaTeX: `latexmk`. Always use with `-interaction=nonstopmode`, `-file-line-error`, `-synctex=1`, and `-outdir=.latexmk_outdir`. Choose compiler flag (`-pdf`, `-xelatex`, or `-lualatex`) based on the document. `-halt-on-error` is recommended; omit only when full log output is needed to systematically diagnose errors. If no user-specified or project-level latexmkrc is present, use `-r .reaslab_meta/tex/latexmkrc`. After a successful compile, the platform copies the PDF next to the source file; open that source-adjacent PDF, not a PDF under `.latexmk_outdir/`.
- Run Python: use `python-execute` (in PATH; run `python-execute --help` for all options), not `python3`/`uv`/`pip`
- Search code: `rg`, `fd`, `jq`, `grep`, `find`
- Open a file in the web UI: `open main.pdf`

After compiling LaTeX, run `open <source-stem>.pdf` from the source file's directory, or pass that
source-adjacent PDF path, to show the PDF in the user's browser.

When the user asks to use MCP, or asks to compile LaTeX or
build Lean via MCP, just run the command directly (`latexmk`,
`lake build`, etc.). All tools are standard shell commands.

### python-execute

`python-execute` is the CLI for running Python in the runtime container.
Invoke it through the shell/terminal tool like any other command.

All Python-related commands (`python3`, `uv`, `pip`, etc.) MUST go through
`python-execute` — never run them directly via the shell tool.

The runtime container has solver packages and their licenses pre-configured
(gurobipy, coptpy, mosek, cplex, ortools, pulp, etc.). Do not attempt to
install, activate, or configure licenses yourself — they are already set up.

Pre-installed packages: numpy, scipy, pandas, matplotlib, gurobipy, coptpy,
mosek, cplex, ortools, pulp, etc.

- `python-execute -c 'print(1+1)'` — run inline code
- `python-execute script.py` — run a file
- `python-execute install <pkg>` — install a package
- `python-execute remove <pkg>` — remove a package
- `python-execute list-packages` — list installed packages
- `python-execute env-status` — check environment and available packages
- `python-execute history` — query execution history
- `python-execute stop <id>` — stop a running execution

### review — read review annotations (IMPORTANT)

This platform has a **Review Panel** where collaborators attach annotations (comments, replies) to selected code/text ranges. These live in a **database**, never in source files.

- `review` — all annotations across every file
- `review <filepath>` — annotations for one file

**CRITICAL RULE**: When the user mentions comments/annotations/feedback in any way (e.g. "who comments the most", "summarize the comments", "show me feedback", "address the comments on X"), you MUST run `review` **immediately as your first action**. Do NOT read source files first. Do NOT ask the user whether to run it — just run it. Even if the user attaches or references a specific file, run `review` (or `review <filepath>`) instead of reading that file. Review annotations are not stored in file contents.

Prefer `review` (all files) first for broad questions ("who comments the most", "summarize all feedback"). Only use `review <filepath>` when the user explicitly asks about one file.

**Output structure** (Markdown grouped by file): each annotation has **author**, **timestamp**, **selected text** (fenced code block), **content** (message body), and **replies** (threaded, each with author + timestamp + content).

Use this data for: summarize all annotations, count/rank by author, find unresolved items (no replies), generate to-do lists, compare across files, etc.

**Exception**: "review" or "feedback" used as a verb ("review my code", "give feedback on this function") means you should analyze the code yourself, not read annotations.

## Skills

Skills are markdown files with YAML frontmatter (name, description).

- Built-in skills: /app/skills/ (packaged in agent image)
- Project skills: <workspace>/skills/
