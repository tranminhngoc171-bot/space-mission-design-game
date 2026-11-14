#!/usr/bin/env bash
# ---------------------------------------------------------------
# sync-to-web.sh — copy the playable build from the team repo to
# the site that serves it (bersious.io.vn/nasa).
#
#   bash scripts/sync-to-web.sh          # copy, then show what changed
#   bash scripts/sync-to-web.sh --check  # do not copy; exit 1 if stale
#
# See docs/10-DEPLOY-TARGET.md. Nothing inside ~/bersious-web/nasa
# should ever be edited by hand — it is generated.
# ---------------------------------------------------------------
set -euo pipefail

TEAM_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${BERSIOUS_WEB:-$HOME/bersious-web}/nasa"
CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

if [[ ! -d "$DEST" ]]; then
  echo "error: destination not found: $DEST" >&2
  echo "       set BERSIOUS_WEB=/path/to/bersious-web if it lives elsewhere" >&2
  exit 2
fi

if [[ "$CHECK_ONLY" == "1" ]]; then
  drift=0
  for f in "$TEAM_REPO"/src/*.js "$TEAM_REPO"/src/css/*.css "$TEAM_REPO"/src/index.html; do
    [[ -e "$f" ]] || continue
    base="$(basename "$f")"
    if [[ -f "$DEST/$base" ]]; then
      cmp -s "$f" "$DEST/$base" || { echo "stale: $base"; drift=1; }
    fi
  done
  for f in "$TEAM_REPO"/data/*.json; do
    [[ -e "$f" ]] || continue
    base="$(basename "$f")"
    if [[ -f "$DEST/data/$base" ]]; then
      cmp -s "$f" "$DEST/data/$base" || { echo "stale: data/$base"; drift=1; }
    else
      echo "missing: data/$base"; drift=1
    fi
  done
  if [[ "$drift" == "1" ]]; then
    echo "→ deployment is OUT OF DATE, run without --check"
    exit 1
  fi
  echo "→ deployment is up to date"
  exit 0
fi

mkdir -p "$DEST/css" "$DEST/data"

# index.html + flat JS modules
for f in "$TEAM_REPO"/src/*.js "$TEAM_REPO"/src/index.html; do
  [[ -e "$f" ]] || continue
  cp -f "$f" "$DEST/$(basename "$f")"
done

# stylesheet
for f in "$TEAM_REPO"/src/css/*.css; do
  [[ -e "$f" ]] || continue
  cp -f "$f" "$DEST/css/$(basename "$f")"
done

# balance data — the numbers must travel with the code
for f in "$TEAM_REPO"/data/*.json; do
  [[ -e "$f" ]] || continue
  cp -f "$f" "$DEST/data/$(basename "$f")"
done

# provenance marker: which commit produced this deployment
SHA="$(git -C "$TEAM_REPO" rev-parse --short HEAD 2>/dev/null || echo unknown)"
BRANCH="$(git -C "$TEAM_REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
{
  echo "# GENERATED — do not edit by hand"
  echo ""
  echo "Source: space-mission-design-game @ \`$SHA\` (branch \`$BRANCH\`)"
  echo "Synced: $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo ""
  echo "Regenerate with \`bash scripts/sync-to-web.sh\` from the team repo."
} > "$DEST/GENERATED.md"

echo "→ synced to $DEST"
echo "→ source commit: $SHA ($BRANCH)"
echo ""
echo "Next:"
echo "  cd $(dirname "$DEST") && git status   # look at what changed"
echo "  git add nasa && git commit -m 'deploy(nasa): sync from team repo @ $SHA' && git push"
