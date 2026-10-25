# Secret Handling Policy
Secrets NEVER enter: model prompts, the Action Ledger, log files, diagnostic
bundles. Locations: kernel keyring (preferred) or 0600 files under
~/.config/aether/secrets. Disk-encryption passphrases live only in the user's
head (and optional recovery file the user creates). Services receive secrets
as function arguments and must not persist them.
