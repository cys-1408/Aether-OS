# Malicious model artifacts

Threat: a tampered or maliciously crafted GGUF/ONNX model, loader, backend
binary or catalog entry ends up on disk and is loaded.

## Controls

1. **Source allow-listing** — downloads originate only from entries in the
   versioned catalog whose source URLs are declared in
   `rootfs/etc/aether/supported-model-sources.yaml` + `ai/catalog/sources-policy.yaml`.
2. **Integrity verification** — `ai/runtime/download/digest_verifier.py` checks
   sha256 against catalog metadata; `manifest_verifier.py` verifies expected
   file lists. No model loads with an unknown digest.
3. **Catalog authenticity** — `ai/runtime/model-catalog/catalog_signature.py`
   verifies the catalog signature before its entries are trusted at all.
4. **Load-time revalidation** — `ai/runtime/validation/model_integrity.py`
   rechecks digests before mmap/load; failed loads quarantine the artifact and
   mark it *failed* in the registry (it is never retried silently).
5. **Loader sandbox** — runtime + backends run under
   `security/sandbox/runtime-sandbox.conf`: no network namespace, writable
   paths limited to the model store + runtime state, syscall filter documented
   in `security/sandbox/syscall-restrictions.md`.
6. **License gate** — `ai/policies/model-license-policy.yaml` blocks artifacts
   without recorded license/usage terms.
7. **Recovery** — Recovery Center → model repair removes quarantined artifacts
   only after user confirmation and preserves unrelated models.
