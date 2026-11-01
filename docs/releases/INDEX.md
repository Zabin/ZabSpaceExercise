[↑ Docs index](../INDEX.md)

# Releases — the release archive

Owner: `11-release-readiness` (its **Release archive** step). Owner decision, 2026-11-01: every release is
**archived as it is released, before any further change is made**, by **tag + release manifest** — git
history is the archive. Each release gets:

- an archive ref on the exact release commit: the branch `archive/release-<n>.<m>`, and the annotated tag
  `release-<n>.<m>` where the environment permits pushing tags (the manifest records when it did not);
- a **Release Manifest** in this folder, `release-<n>.<m>.md`: commit, archive refs, assessment links,
  counts, dependency lock, known deviations, reviews relied on, merged branches, owner decisions, how to
  run, and the trust model.

## Releases

| Release | Date | Commit | Archive ref | Manifest |
|---|---|---|---|---|
| 1.0 | 2026-11-01 | `82436ba` | `archive/release-1.0` (tag `release-1.0`: pending) | [release-1.0.md](release-1.0.md) |

## How to restore a release

```bash
git fetch origin
git checkout archive/release-1.0        # the archive branch ref (always present)
git checkout release-1.0                # the annotated tag, once it exists on the remote
git checkout -b maint/release-1.0 archive/release-1.0   # a maintenance (hotfix) branch from the archive
```

Then follow the manifest's "How to run" (install from the release's own `requirements.lock`).

Optional offline copy: `git bundle create release-1.0.bundle archive/release-1.0`, restored with
`git clone release-1.0.bundle spacesim-1.0`.
