# Certificate Policy
TLS verification: system CA bundle via urllib default context — never
certificate verification disabled. Pinning: model catalog + repo metadata are
verified by digest + signature instead of TLS pinning. Key rotation:
security/cryptography/key-rotation-policy.md.
