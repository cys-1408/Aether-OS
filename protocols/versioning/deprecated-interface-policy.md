# Deprecated Interface Policy
1. Deprecation notice in CHANGELOG + docs at version N.
2. Interface keeps working through N+1 with a logged warning (AETHER_LOG_DEPRECATED=1 surfaces loudly).
3. Removal only in the next major version, with a migration note in docs/interfaces/compatibility-policy.md.
4. Every service answers `X.info` with {service, api_version} so callers can branch.
