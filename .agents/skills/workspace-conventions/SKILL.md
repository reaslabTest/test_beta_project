---
name: workspace-conventions
description: Conventions for tools, skills, and project state in ReasLab workspaces.
---

## Tools

Standard shell tools are available in PATH. Use them directly.

- Build Lean projects: `lake build`, `lake build Mathlib.Order.Basic`
- Compile LaTeX: `latexmk`. Always use with `-interaction=nonstopmode`, `-file-line-error`, `-synctex=1`, and `-outdir=.latexmk_outdir` (the platform reads the PDF from there; passing it explicitly keeps output in the right place even when no latexmkrc is found). Choose compiler flag (`-pdf`, `-xelatex`, or `-lualatex`) based on the document. `-halt-on-error` is recommended; omit only when full log output is needed to systematically diagnose errors. If no user-specified or project-level latexmkrc is present, use `-r .reaslab_meta/tex/latexmkrc`.
- Run Python: use `python-execute` (in PATH; run `python-execute --help` for all options), not `python3`/`uv`/`pip`
- Search code: `rg`, `fd`, `jq`, `grep`, `find`
- Open a file in the web UI: `open main.pdf`

After compiling LaTeX, run `open main.pdf` to show the PDF
in the user's browser.

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

## Skills

Skills are markdown files with YAML frontmatter (name, description).

- Built-in skills: /app/skills/ (packaged in agent image)
- Project skills: <workspace>/skills/
