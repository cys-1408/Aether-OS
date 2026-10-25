# Catalog Format
catalog.json (schema: ai/catalog/catalog.schema.json) lists curated GGUF models:
model_id, name, task_classes, repo/file (Hugging Face), quantization,
approx_size_gb (explicitly approximate), license, context_lengths, min_ram_gb.
Integrity: catalog.json.sha256 is required (verified at load); optional
catalog.json.sig enables GPG verification when the release key is imported.
Weight digests are NOT stored here — they are obtained from the HF API at
download time (lfs.sha256) and verified streamingly (docs/ai/model-catalog-format.md).
