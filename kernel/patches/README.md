# Patch Policy (binding)

A patch may be added only if it: (1) fixes a demonstrable defect or enables
required hardware not served upstream; (2) is under 200 lines; (3) carries a
template entry below with rationale, upstream status (submitted? link?),
threat review and an explicit removal path; (4) is recorded in
`provenance/patch-manifest.json` by `scripts/collect-provenance.sh`.

Template:
    patch-name.patch  — one-line summary
      rationale: ...
      upstream-status: submitted|accepted|rejected|not-applicable
      threat-review: ...
      removal-path: dropped when upstream <link> lands
