# AI Usage — Lab 1

**Model used:** Claude (Anthropic), via the Claude Code CLI, Sonnet 5 model.

I used Claude to diagnose two environment errors I hit while setting up the
`uv` environment for this lab. For each one I first asked Claude *what the
error meant*, and only after I understood it did I ask *how to fix it* —
then I checked the fix myself before trusting it. The two interactions are
written up below.

---

## Interaction 1 — dependency resolution conflict (`uv add`)

### What I did

Following the "break it on purpose" step from the Week 2 practical, I added
a deliberately incompatible dependency to see what a real resolver conflict
looks like:

```bash
uv add "numpy==1.19.0"
```

### The exact error

```text
  × No solution found when resolving dependencies for split (markers:
  │ python_full_version >= '3.14' and sys_platform == 'win32'):
  ╰─▶ Because only pandas<=3.0.5 is available and pandas==3.0.5 depends
      on numpy{python_full_version >= '3.14'}>=2.3.3, we can conclude that
      pandas>=3.0.5 depends on numpy>=2.3.3.
      And because your project depends on numpy==1.19.0 and pandas>=3.0.5, we
      can conclude that your project's requirements are unsatisfiable.

      hint: While the active Python version is 3.13, the resolution failed for
      other Python versions supported by your project. Consider limiting your
      project's supported Python versions using `requires-python`.
  help: If you want to add the package regardless of the failed resolution,
        provide the `--frozen` flag to skip locking and syncing.
```

### Question 1 — "what does this mean?"

I pasted the full error into Claude and asked what it was telling me,
before asking for any fix. Claude's explanation: `uv` could not find a
single set of versions that satisfies every constraint at once. My
`pyproject.toml` already requires `pandas>=3.0.5`, and pandas 3.0.5 itself
requires `numpy>=2.3.3`, so pinning `numpy==1.19.0` on top of that is a
direct contradiction — "unsatisfiable" is the resolver telling me two
things I asked for can't both be true, not a bug or a network problem.
Claude also explained the `--frozen` hint is an escape hatch that would
only paper over the conflict (install anyway, skip locking), not fix it,
so I should not use it here.

### Question 2 — "how do I fix it?"

Claude said the fix depends on intent: if I actually needed old numpy I'd
have to drop the pandas 3 requirement; since I don't, the right move is to
simply remove the bad pin and let `uv` resolve numpy transitively from
pandas. It suggested that because `uv add` is atomic on a failed
resolution, `pyproject.toml` was probably already untouched and I might
not need to undo anything.

### How I verified before trusting it

1. I ran `cat pyproject.toml` and confirmed Claude was right that the
   failed `uv add` had rolled itself back — `numpy` was not in the file,
   only `pandas>=3.0.5`.
2. I did a full clean rebuild to prove the environment was actually intact:
   `rm -rf .venv && uv sync --locked && uv run python src/analysis.py`.
3. I compared that run's output line-by-line against the output from
   before I broke anything (`pandas 3.0.5`, `mean 56.00`, the by-site and
   by-cohort tables). They matched exactly, so the environment was back to
   a known-good state.

I kept: the explanation of *why* it was unsatisfiable, and the advice not
to use `--frozen`. I rejected nothing outright, but I did not take
"probably already rolled back" on faith — I checked the file myself.

---

## Interaction 2 — lockfile out of date (`uv sync --locked`)

### What I did

I hand-edited `pyproject.toml` to add another package (`tabulate>=0.9`) and
then immediately tried to sync with `--locked`, forgetting that editing the
manifest by hand does not update `uv.lock`:

```bash
uv sync --locked
```

### The exact error

```text
Resolved 7 packages in 147ms
The lockfile at `uv.lock` needs to be updated, but `--locked` was provided. To update the lockfile, run `uv lock`.
```

### Question 1 — "what does this mean?"

I asked Claude what `--locked` was actually checking. Its explanation:
`--locked` is an assertion — "the lockfile is already consistent with
`pyproject.toml`, just install it, and error if that's not true." Because I
had added `tabulate` to `pyproject.toml` without re-locking, the manifest
and `uv.lock` disagreed, so the assertion failed on purpose. This is the
behaviour you *want* in CI and in a grader's clean checkout: it refuses to
silently install something different from what's pinned.

### Question 2 — "how do I fix it?"

Claude said there are two different fixes and they are not the same:
- `uv lock` (or `uv add tabulate`) to *accept* the change and regenerate
  `uv.lock`, then commit both files together; or
- revert the `pyproject.toml` edit if the change was a mistake, so the
  lockfile and manifest agree again.

Since `tabulate` was just me experimenting and my script doesn't use it, I
took the second path.

### How I verified before trusting it

1. I restored the original `pyproject.toml` (`pandas` only).
2. I re-ran `rm -rf .venv && uv sync --locked` — this time it succeeded
   with no "needs to be updated" message, confirming manifest and lockfile
   agreed again.
3. I ran `uv run python src/analysis.py` and confirmed the summary output
   was identical to the committed expected output in `README.md`.
4. I ran `git status` to make sure `pyproject.toml` and `uv.lock` were back
   to their committed state and I wasn't about to commit a stray
   `tabulate` line.

Takeaway I kept for the rest of the lab: always change dependencies with
`uv add` / `uv remove` (which lock automatically), not by hand-editing
`pyproject.toml`, and commit `pyproject.toml` and `uv.lock` in the same
commit.
