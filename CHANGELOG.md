# Changelog

## 1.0.0 (Aurora) — 2026-10-24
Initial complete implementation of the Aether Cognitive Operating System.

### Added
- Bootable ISO build pipeline (build/scripts/00..99) producing a hybrid UEFI+BIOS image with live, installer and recovery entries.
- Pinned upstream Linux 6.12 LTS kernel with Aether configuration fragments, provenance collection and verification scripts.
- Native desktop: sway compositor session, GTK3 aether-shell (top bar, taskbar, desktop icons, launcher, notification center, activity panel, focus chip, toasts), Miso companion with idle/walk/run/jump/search/sleep/carry states, speech bubble and reduced-motion support.
- Core services: hardware probe, power, accounts/sessions, mount manager, trash, networking, firewall, network consent, audio, voice input, clock/reminders, notifications, clipboard, printing, logging/diagnostics, backup.
- Aether Runtime: hardware profiling, curated catalog, recommendation, consent-gated download with digest verification, llama.cpp backend adapter, inference scheduler, resource governor, smoke-check validation.
- IntentFS: inotify watcher, extraction pipeline, exactly-three-concept generation with bounded retry, SQLite index, explainable search, privacy exclusions.
- Miso agent + CapabilityOS: capability catalogs, broker with policy engine and confirmation flow, Action Ledger, Living Workspaces with restore preview, presence events, prompt-injection defenses.
- Installer with explicit destructive-action guard, optional LUKS2 encryption, first-boot wizard; recovery environment with repair/rollback/diagnostics; pacman-based package manager and staged signed updates.
- Accessibility: keyboard navigation, AT-SPI bridge, high contrast, font scaling, text-only mode.

### Notes
- The ISO artifact itself is produced by `make iso` on a Linux build host; see docs/user/installation-guide.md.
