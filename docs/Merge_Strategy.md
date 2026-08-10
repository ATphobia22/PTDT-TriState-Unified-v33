# Branch Merge Strategy (PTDT-TriState-Unified-v33)

## Current state
- **`main`** is the production line (cinematic twin, PostGIS, Windows build).
- Many `feature/hydraulic-groundwater-authority*` branches share identical commits — treat as one logical feature, not N merges.
- `dependabot/*` — dependency bumps; merge only after `npm i` + `npm run build` succeeds.
- `atphobia22-shiny-succotash` — experimental; cherry-pick or PR only if needed.

## Policy
1. **All new work lands on `main`** via direct push or short-lived feature → PR → squash merge.
2. **Do not bulk-merge** duplicate hydraulic branches; they add no unique tip history and risk noise/conflicts.
3. **Squash merge** preferred for feature PRs (clean history).
4. **Rebase** dependabot onto latest `main` before merge.
5. After merge, delete the head branch.

## One-time cleanup (optional, local git)
```powershell
git fetch --all
# list merged / stale
git branch -r --merged origin/main
# delete remote stale feature (example)
# gh api -X DELETE repos/ATphobia22/PTDT-TriState-Unified-v33/git/refs/heads/feature/hydraulic-groundwater-authority-v2
```

## Conflict rule
If a feature branch diverges: open PR → resolve on GitHub → squash into `main`. Never force-push `main`.
