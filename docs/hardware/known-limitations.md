# Known Limitations (1.0.0)
- Secure Boot requires user-managed keys; no shipped shim.
- NVIDIA proprietary driver not packaged; nouveau/modesetting only.
- OCR, PDF extraction and voice transcription require optional packages (tesseract, poppler, whisper.cpp) — features degrade truthfully without them.
- IntentFS is metadata-level; no kernel filesystem integration in 1.0.0.
- Hibernate requires swap and firmware support; suspend is the supported path.
- ARM64 is not a supported target in 1.0.0.
