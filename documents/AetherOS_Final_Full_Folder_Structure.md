# AETHER --- Final Standalone Operating System Folder Structure

**Target:** a complete, independently bootable Aether OS distribution
delivered as an installable ISO\
**Architecture:** upstream Linux kernel + Aether-maintained
configuration/patches + native system services + native desktop\
**Reference basis:** `Aether_Full_Project_Description(1).docx`,
especially kernel/boot (pp. 7--9), OS subsystems (pp. 9--10), Runtime
(pp. 11--12), IntentFS (pp. 12--14), Miso/CapabilityOS (pp. 14--16),
native desktop/apps (pp. 16--20),
installation/recovery/security/accessibility (pp. 20--26).

## Non-negotiable implementation rules

-   This is a standalone operating system, not a website, browser
    desktop, web app, theme, or add-on OS.
-   The deliverable includes a real boot chain, Linux kernel, initramfs,
    root filesystem, native services, login/session manager, native
    graphical desktop, working applications, installer, recovery
    environment, package/update infrastructure, and reproducible ISO
    build system.
-   Linux kernel directory names below are a **layout reference only**.
    Kernel source files are not to be recreated from their names. Import
    a maintained upstream Linux source tree, preserve its real code and
    licenses, maintain Aether configuration and a small explicit patch
    series, and build it using the documented toolchain.
-   AI inference, Miso planning, IntentFS indexing, and policy decisions
    run in user space. No LLM is placed in scheduler, interrupt, memory
    allocator, or other kernel-critical paths.
-   Aether Runtime is Aether-owned and does not require Ollama. It may
    integrate a pluggable inference backend behind Aether's own API.
-   A supported indexed file receives exactly three validated, distinct
    local-model-predicted concepts. Failed indexing remains visibly
    pending/failed; do not fabricate concepts.
-   Every visible control must work against a real service or be
    explicitly disabled with a reason. No mock filesystem, fake
    terminal, hard-coded telemetry, pretend action success, or
    placeholder apps.
-   Build outputs, downloaded model weights, user data, secrets, signing
    keys, and generated binaries are not committed as source files. They
    belong in build output, controlled runtime storage, or protected key
    storage.

## Legend

`path/to/file — purpose` describes the responsibility of a file.
Directory entries are explained at the nearest parent. `*.service`,
`*.conf`, `*.yaml`, `*.json`, `*.policy`, and similar names are intended
as real configuration/interface files, not empty placeholders. The
implementation team may adjust exact filenames to chosen upstream tools,
but must preserve the responsibilities and integration boundaries.

# 1. Repository root

``` text
AetherOS/
├── README.md
├── LICENSES.md
├── NOTICE
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── VERSION
├── CHANGELOG.md
├── Makefile
├── justfile
├── .gitignore
├── .editorconfig
├── .clang-format
├── .rustfmt.toml
├── .shellcheckrc
├── .gitmodules
├── .reuse/dep5
├── docs/
├── configs/
├── kernel/
├── boot/
├── toolchain/
├── build/
├── packaging/
├── rootfs/
├── system/
├── services/
├── libraries/
├── protocols/
├── desktop/
├── applications/
├── ai/
├── intentfs/
├── miso/
├── security/
├── networking/
├── hardware/
├── installer/
├── recovery/
├── updater/
├── package-manager/
├── accessibility/
├── localization/
├── data/
├── assets/
├── firmware/
├── third-party/
├── release/
└── artifacts/                 # generated output; normally ignored by version control
```

-   `README.md` --- project overview, supported machine profile,
    boot/install summary, source build entry point.
-   `LICENSES.md` / `NOTICE` --- project and third-party license notices
    and attribution.
-   `SECURITY.md` --- vulnerability reporting, threat model location,
    supported release/security policy.
-   `VERSION` / `CHANGELOG.md` --- release identity and user-visible
    changes.
-   `Makefile` / `justfile` --- stable developer commands for fetching
    sources, building packages, assembling rootfs and producing ISO.
-   `.gitmodules` --- pinned upstream source references where submodules
    are used; never use an unpinned moving branch for release builds.
-   `artifacts/` --- generated kernel images, packages, rootfs staging,
    ISO and checksums; not hand-maintained source.

# 2. Documentation tree

``` text
docs/
├── architecture/
│   ├── system-overview.md
│   ├── boot-chain.md
│   ├── kernel-boundary.md
│   ├── process-and-service-map.md
│   ├── ipc-and-dbus.md
│   ├── privilege-boundaries.md
│   ├── data-flow.md
│   └── failure-domains.md
├── kernel/
│   ├── upstream-selection.md
│   ├── config-policy.md
│   ├── patch-policy.md
│   ├── driver-support.md
│   ├── build-provenance.md
│   └── update-and-cve-process.md
├── boot-and-install/
│   ├── firmware-matrix.md
│   ├── bootloader-layout.md
│   ├── initramfs-design.md
│   ├── installer-flow.md
│   ├── partitioning-and-encryption.md
│   ├── first-boot.md
│   └── recovery.md
├── desktop/
│   ├── native-shell.md
│   ├── visual-design-system.md
│   ├── window-management.md
│   ├── miso-animation-spec.md
│   └── accessibility-contract.md
├── ai/
│   ├── runtime-architecture.md
│   ├── hardware-profiling.md
│   ├── model-catalog-format.md
│   ├── inference-api.md
│   ├── backend-adapter-contract.md
│   ├── resource-governor.md
│   └── offline-operation.md
├── intentfs/
│   ├── metadata-schema.md
│   ├── extraction-policy.md
│   ├── exactly-three-concepts.md
│   ├── search-ranking.md
│   └── privacy-and-exclusions.md
├── miso/
│   ├── agent-loop.md
│   ├── capability-catalog.md
│   ├── broker-policy.md
│   ├── action-ledger.md
│   ├── prompt-injection-defense.md
│   └── undo-and-recovery.md
├── security/
│   ├── threat-model.md
│   ├── secure-boot-and-signing.md
│   ├── secrets-management.md
│   ├── application-sandboxing.md
│   ├── privacy-defaults.md
│   └── incident-response.md
├── operations/
│   ├── package-format.md
│   ├── repository-signing.md
│   ├── atomic-update-and-rollback.md
│   ├── backup-and-restore.md
│   ├── logging-and-diagnostics.md
│   └── release-process.md
├── interfaces/
│   ├── dbus-names.md
│   ├── api-versioning.md
│   ├── capability-schema.md
│   └── compatibility-policy.md
├── hardware/
│   ├── supported-hardware.md
│   ├── firmware-licensing.md
│   └── known-limitations.md
├── decisions/
│   ├── ADR-0001-linux-kernel.md
│   ├── ADR-0002-native-desktop-stack.md
│   ├── ADR-0003-init-system.md
│   ├── ADR-0004-package-format.md
│   ├── ADR-0005-inference-backend.md
│   └── ADR-0006-system-update-strategy.md
└── user/
    ├── installation-guide.md
    ├── first-boot-guide.md
    ├── desktop-guide.md
    ├── ai-runtime-guide.md
    ├── privacy-guide.md
    ├── troubleshooting.md
    └── recovery-guide.md
```

# 3. Linux kernel source reference tree

`kernel/linux/` is the actual upstream Linux source checkout. The
following familiar directory names are a structural reference to the
upstream tree, not a request to implement a kernel from filenames. Keep
the upstream source intact and record the exact release, commit,
signature and patches.

``` text
kernel/
├── README.md
├── upstream.lock
├── source/
│   └── linux/                         # fetched/pinned upstream Linux tree
├── configs/
│   ├── aether_defconfig
│   ├── fragments/
│   │   ├── cpu-and-scheduler.config
│   │   ├── memory-and-cgroups.config
│   │   ├── storage-and-filesystems.config
│   │   ├── networking.config
│   │   ├── graphics-drm.config
│   │   ├── input-and-hid.config
│   │   ├── audio.config
│   │   ├── security-and-lsm.config
│   │   ├── namespaces-and-seccomp.config
│   │   ├── power-thermal.config
│   │   └── debug-and-diagnostics.config
│   └── supported-hardware.config
├── patches/
│   ├── series
│   ├── README.md
│   └── <reviewed-aether-patch>.patch
├── scripts/
│   ├── fetch-upstream.sh
│   ├── verify-upstream.sh
│   ├── apply-patches.sh
│   ├── merge-config.sh
│   ├── build-kernel.sh
│   └── collect-provenance.sh
├── provenance/
│   ├── upstream-commit.txt
│   ├── patch-manifest.json
│   ├── config-hash.txt
│   └── toolchain-manifest.json
└── notes/
    ├── config-rationale.md
    ├── patch-rationale.md
    └── release-cve-status.md
```

## Upstream Linux kernel directories to preserve as found

``` text
kernel/source/linux/
├── arch/          # architecture-specific boot, CPU, MMU and platform support
├── block/         # block I/O layer
├── certs/         # kernel certificate/key support; release key handling remains controlled
├── crypto/        # kernel crypto APIs and algorithms
├── Documentation/
├── drivers/
├── fs/
├── include/
├── init/
├── ipc/
├── kernel/
├── lib/
├── mm/
├── net/
├── samples/
├── scripts/
├── security/
├── sound/
├── tools/
├── usr/
├── virt/
├── Kbuild
├── Kconfig
├── MAINTAINERS
├── Makefile
└── README
```

Kernel reference subdirectories worth knowing (do not recreate these
manually):

-   `arch/x86/` --- x86 platform and boot support for an x86-64 target.
-   `arch/arm64/` --- optional ARM64 target only if Aether explicitly
    supports it.
-   `drivers/acpi/`, `drivers/base/`, `drivers/block/`,
    `drivers/gpu/drm/`, `drivers/hid/`, `drivers/input/`,
    `drivers/net/`, `drivers/nvme/`, `drivers/pci/`,
    `drivers/platform/`, `drivers/rtc/`, `drivers/scsi/`,
    `drivers/thermal/`, `drivers/usb/`, `drivers/video/`,
    `drivers/watchdog/` --- upstream driver families.
-   `fs/` --- VFS and filesystem implementations. IntentFS does not
    replace this kernel layer.
-   `include/linux/` --- kernel interfaces and headers.
-   `init/` --- kernel initialization code.
-   `ipc/` --- kernel IPC primitives.
-   `kernel/` --- core process, scheduler, locking, timer and other
    kernel subsystems.
-   `mm/` --- virtual memory and memory-management implementation.
-   `net/` --- network stack.
-   `security/` --- kernel security hooks/LSM infrastructure.
-   `sound/` --- ALSA kernel sound subsystem.
-   `tools/` --- upstream kernel tools and utilities.
-   `virt/` --- virtualization support.

# 4. Boot, firmware and ISO production

``` text
boot/
├── README.md
├── grub/
│   ├── grub.cfg.in
│   ├── grub-install.conf
│   ├── menu-entry-normal.cfg
│   ├── menu-entry-recovery.cfg
│   └── theme/
│       ├── theme.txt
│       ├── background.png
│       └── icons/
├── initramfs/
│   ├── README.md
│   ├── init
│   ├── modules-load.conf
│   ├── storage-discovery.conf
│   ├── cryptsetup.conf
│   ├── root-mount.conf
│   ├── switch-root.conf
│   └── hooks/
│       ├── 10-device-discovery
│       ├── 20-storage-drivers
│       ├── 30-filesystem-drivers
│       ├── 40-encryption
│       ├── 50-root-selection
│       └── 90-switch-root
├── kernel-cmdline/
│   ├── normal.conf
│   ├── installer.conf
│   └── recovery.conf
└── firmware-policy/
    ├── firmware-manifest.yaml
    └── redistribution-notes.md

toolchain/
├── README.md
├── versions.lock
├── host-prerequisites.md
├── cross/
│   ├── x86_64-toolchain.cmake
│   └── toolchain-manifest.json
├── sysroot/
│   └── README.md
└── scripts/
    ├── verify-toolchain.sh
    ├── build-binutils.sh
    ├── build-compiler.sh
    └── verify-reproducibility.sh

build/
├── README.md
├── profiles/
│   ├── desktop-x86_64.yaml
│   ├── installer-x86_64.yaml
│   └── recovery-x86_64.yaml
├── manifests/
│   ├── base-packages.yaml
│   ├── desktop-packages.yaml
│   ├── ai-packages.yaml
│   ├── firmware-packages.yaml
│   └── excluded-packages.yaml
├── scripts/
│   ├── 00-check-host.sh
│   ├── 10-fetch-sources.sh
│   ├── 20-build-kernel.sh
│   ├── 30-build-packages.sh
│   ├── 40-assemble-rootfs.sh
│   ├── 50-build-initramfs.sh
│   ├── 60-stage-bootloader.sh
│   ├── 70-build-live-environment.sh
│   ├── 80-build-installer-image.sh
│   ├── 90-create-iso.sh
│   ├── 95-generate-checksums.sh
│   └── 99-create-release-manifest.sh
├── rootfs/
│   ├── directory-layout.yaml
│   ├── permissions-manifest.yaml
│   └── default-config-manifest.yaml
├── iso/
│   ├── iso-layout.yaml
│   ├── boot-catalog.conf
│   └── volume-label.conf
└── reproducibility/
    ├── environment.lock
    ├── source-hashes.txt
    └── build-metadata.schema.json

release/
├── README.md
├── release-manifest.schema.json
├── signing-policy.md
├── sbom/
├── checksums/
├── signatures/
├── package-index/
├── source-manifest/
├── licenses/
└── notes/
```

-   `boot/grub/grub.cfg.in` --- produces boot menu entries for normal
    startup, installer and recovery; selects kernel/initramfs and safe
    parameters.
-   `boot/initramfs/init` --- minimal early userspace entry point:
    discover storage, unlock configured encrypted root, mount root and
    switch to real root.
-   `build/scripts/90-create-iso.sh` --- assembles a real hybrid
    bootable ISO from built system artifacts; it does not package a
    website as an operating system.
-   `build/scripts/95-generate-checksums.sh` --- emits cryptographic
    checksums for release artifacts.
-   `release/signing-policy.md` --- defines how release artifacts and
    repository metadata are signed without committing private signing
    keys.

# 5. Root filesystem layout

The image's installed/live root filesystem must provide a standard,
maintainable Linux hierarchy. This is the filesystem layout inside
Aether, not a duplicate source-code tree.

``` text
rootfs/
├── etc/
│   ├── aether/
│   │   ├── os-release.d
│   │   ├── system.yaml
│   │   ├── first-boot.yaml
│   │   ├── privacy-defaults.yaml
│   │   ├── runtime.yaml
│   │   ├── intentfs.yaml
│   │   ├── miso.yaml
│   │   ├── capability-policy.yaml
│   │   ├── update-policy.yaml
│   │   └── supported-model-sources.yaml
│   ├── os-release
│   ├── hostname
│   ├── hosts
│   ├── fstab
│   ├── crypttab
│   ├── passwd
│   ├── group
│   ├── shadow                    # generated securely on installed system; never commit real credentials
│   ├── sudoers.d/
│   ├── sysctl.d/
│   ├── modprobe.d/
│   ├── udev/
│   ├── security/
│   ├── pam.d/
│   ├── polkit-1/
│   ├── dbus-1/
│   ├── NetworkManager/
│   ├── pipewire/
│   ├── systemd/                  # or equivalent chosen init/service manager configuration
│   ├── skel/
│   └── issue
├── boot/
│   ├── vmlinuz-aether
│   ├── initramfs-aether.img
│   └── grub/
├── dev/
├── proc/
├── sys/
├── run/
├── tmp/
├── usr/
│   ├── bin/
│   ├── sbin/
│   ├── lib/
│   ├── libexec/
│   ├── include/
│   ├── share/
│   └── local/
├── var/
│   ├── cache/
│   ├── lib/
│   │   ├── aether/
│   │   ├── package-manager/
│   │   └── systemd/
│   ├── log/
│   ├── spool/
│   └── tmp/
├── home/
├── root/
├── opt/
│   └── aether/
├── srv/
├── mnt/
├── media/
└── lost+found/
```

Responsibilities: - `/etc/aether/` --- system-wide defaults only; user
preferences live under each user's configuration directory. -
`/usr/bin/` and `/usr/libexec/aether/` --- installed executable entry
points and internal service helpers. - `/usr/lib/aether/` --- shared
runtime libraries and service modules. - `/usr/share/aether/` --- icons,
desktop entries, schemas, translations, policy documentation and model
catalog metadata. - `/var/lib/aether/` --- root-owned service state,
package metadata, model manifests and system-level databases. -
`/var/log/` or journal storage --- system logs with retention and
permissions. - `/home/<user>/.config/aether/` --- user preferences and
session settings. - `/home/<user>/.local/share/aether/` --- user-scoped
Action Ledger, IntentFS index and workspace data. -
`/var/lib/aether/models/` or a configured user model directory ---
versioned model files; separate from OS packages and never executable as
native code merely because they are model files.

# 6. Base system and service manager

``` text
system/
├── init/
│   ├── README.md
│   ├── service-manager-policy.conf
│   ├── boot-targets.conf
│   ├── dependency-graph.yaml
│   └── shutdown-order.yaml
├── services/
│   ├── aether-firstboot.service
│   ├── aether-hardware-probe.service
│   ├── aether-network-policy.service
│   ├── aether-session.service
│   ├── aether-runtime.service
│   ├── aether-broker.service
│   ├── aether-agent.service
│   ├── aether-intentfs.service
│   ├── aether-ledger.service
│   ├── aether-workspace.service
│   ├── aether-notification.service
│   ├── aether-update-check.service
│   ├── aether-health.service
│   ├── aether-backup.service
│   ├── aether-recovery.service
│   └── aether-cleanup.service
├── targets/
│   ├── aether-graphical.target
│   ├── aether-installer.target
│   ├── aether-recovery.target
│   └── aether-firstboot.target
├── timers/
│   ├── aether-index-reconcile.timer
│   ├── aether-update-check.timer
│   ├── aether-maintenance.timer
│   └── aether-backup-reminder.timer
├── udev/
│   ├── 60-aether-removable-media.rules
│   ├── 70-aether-input.rules
│   └── 80-aether-hardware-events.rules
├── sysctl/
│   ├── 10-aether-network-hardening.conf
│   ├── 20-aether-memory-policy.conf
│   └── 30-aether-kernel-hardening.conf
├── logging/
│   ├── journald.conf
│   ├── log-retention.conf
│   ├── redaction-rules.yaml
│   └── diagnostic-export-policy.yaml
└── health/
    ├── service-health.schema.json
    ├── health-check-policy.yaml
    └── failure-recovery-map.yaml
```

-   `aether-firstboot.service` --- launches setup once, persists
    completion and safely resumes if interrupted.
-   `aether-hardware-probe.service` --- reports detected facts and
    unknown values from supported system interfaces.
-   `aether-health.service` --- monitors actual service state and emits
    actionable, rate-limited events.
-   `aether-cleanup.service` --- cleans only explicitly eligible
    caches/temp files; it never silently deletes user files.
-   Service definitions must include users, groups, sandboxing, restart
    behavior, dependencies, resource limits and logs.

# 7. Core system services

``` text
services/
├── common/
│   ├── service_main.*
│   ├── service_config.*
│   ├── service_logging.*
│   ├── service_errors.*
│   ├── service_health.*
│   ├── shutdown_handler.*
│   └── version_info.*
├── hardware/
│   ├── hardware-probe/
│   │   ├── main.*
│   │   ├── cpu_probe.*
│   │   ├── memory_probe.*
│   │   ├── accelerator_probe.*
│   │   ├── storage_probe.*
│   │   ├── network_probe.*
│   │   ├── audio_probe.*
│   │   ├── display_probe.*
│   │   ├── thermal_probe.*
│   │   ├── battery_probe.*
│   │   ├── firmware_probe.*
│   │   └── hardware_profile.schema.json
│   ├── device-events/
│   │   ├── device_monitor.*
│   │   ├── device_permissions.*
│   │   └── removable_media_policy.*
│   └── power-manager/
│       ├── power_manager.*
│       ├── power_profiles.*
│       ├── suspend_resume.*
│       ├── battery_policy.*
│       └── thermal_policy.*
├── account/
│   ├── account-service/
│   │   ├── main.*
│   │   ├── user_create.*
│   │   ├── group_policy.*
│   │   ├── password_policy.*
│   │   └── account_events.*
│   ├── authentication/
│   │   ├── auth_provider.*
│   │   ├── lock_screen_policy.*
│   │   └── session_auth.*
│   └── session/
│       ├── session_manager.*
│       ├── login_flow.*
│       ├── logout_flow.*
│       ├── session_restore.*
│       └── session_state.schema.json
├── storage/
│   ├── mount-manager/
│   │   ├── mount_service.*
│   │   ├── partition_discovery.*
│   │   ├── removable_mount_policy.*
│   │   ├── safe_eject.*
│   │   └── mount_events.*
│   ├── disk-health/
│   │   ├── disk_health.*
│   │   └── health_capabilities.*
│   └── trash/
│       ├── trash_service.*
│       ├── restore_service.*
│       └── trash_metadata.schema.json
├── networking/
│   ├── network-service/
│   │   ├── network_service.*
│   │   ├── connection_state.*
│   │   ├── wifi_adapter.*
│   │   ├── ethernet_adapter.*
│   │   ├── vpn_adapter.*
│   │   └── network_status.schema.json
│   ├── firewall/
│   │   ├── firewall_policy.*
│   │   ├── rule_manager.*
│   │   └── policy_validation.*
│   └── network-consent/
│       ├── transfer_consent.*
│       └── per_capability_network_policy.*
├── audio/
│   ├── audio-service/
│   │   ├── audio_service.*
│   │   ├── device_selection.*
│   │   ├── volume_control.*
│   │   ├── per_app_audio.*
│   │   └── microphone_permission.*
│   └── voice-input/
│       ├── voice_input.*
│       ├── speech_backend_adapter.*
│       └── microphone_state.*
├── time/
│   ├── clock-service/
│   │   ├── clock_service.*
│   │   ├── timezone_service.*
│   │   ├── time_sync.*
│   │   ├── timer_service.*
│   │   └── locale_format.*
│   └── scheduler/
│       ├── reminder_service.*
│       └── reminder_record.schema.json
├── notifications/
│   ├── notification_service.*
│   ├── notification_policy.*
│   ├── notification_rate_limit.*
│   └── notification.schema.json
├── clipboard/
│   ├── clipboard_service.*
│   ├── history_policy.*
│   └── sensitive_content_filter.*
├── printing/
│   ├── print_service.*
│   ├── queue_manager.*
│   ├── scan_service.*
│   └── device_discovery.*
├── logging/
│   ├── journal_adapter.*
│   ├── log_query.*
│   ├── diagnostic_bundle.*
│   └── secret_redactor.*
└── backup/
    ├── backup_service.*
    ├── backup_scheduler.*
    ├── restore_service.*
    ├── snapshot_adapter.*
    └── backup_manifest.schema.json
```

# 8. Shared libraries and IPC contracts

``` text
libraries/
├── libaether-core/
│   ├── include/aether_core/
│   │   ├── result.h
│   │   ├── error.h
│   │   ├── version.h
│   │   ├── cancellation.h
│   │   ├── timeout.h
│   │   └── resource_limits.h
│   ├── src/
│   │   ├── result.*
│   │   ├── error.*
│   │   ├── cancellation.*
│   │   └── resource_limits.*
│   └── CMakeLists.txt
├── libaether-ipc/
│   ├── include/aether_ipc/
│   │   ├── client.h
│   │   ├── server.h
│   │   ├── authentication.h
│   │   ├── message_envelope.h
│   │   └── schema_validation.h
│   ├── src/
│   └── CMakeLists.txt
├── libaether-config/
│   ├── include/aether_config/config_store.h
│   ├── src/config_store.*
│   ├── src/config_migration.*
│   └── schemas/
├── libaether-files/
│   ├── include/aether_files/file_identity.h
│   ├── include/aether_files/file_ops.h
│   ├── src/file_identity.*
│   ├── src/file_ops.*
│   └── src/permission_check.*
├── libaether-ui/
│   ├── include/aether_ui/theme.h
│   ├── include/aether_ui/accessibility.h
│   ├── src/theme.*
│   ├── src/keyboard_navigation.*
│   └── src/reduced_motion.*
└── libaether-telemetry/
    ├── include/aether_telemetry/metrics.h
    ├── src/system_metrics.*
    └── src/metrics_redaction.*

protocols/
├── dbus/
│   ├── org.aether.Runtime.xml
│   ├── org.aether.IntentFS.xml
│   ├── org.aether.CapabilityBroker.xml
│   ├── org.aether.ActionLedger.xml
│   ├── org.aether.Workspaces.xml
│   ├── org.aether.Settings.xml
│   ├── org.aether.Updates.xml
│   ├── org.aether.Notifications.xml
│   └── org.aether.SystemStatus.xml
├── schemas/
│   ├── capability-request.schema.json
│   ├── capability-result.schema.json
│   ├── action-plan.schema.json
│   ├── action-ledger-entry.schema.json
│   ├── hardware-profile.schema.json
│   ├── model-profile.schema.json
│   ├── inference-request.schema.json
│   ├── inference-response.schema.json
│   ├── intentfs-record.schema.json
│   ├── workspace.schema.json
│   ├── notification.schema.json
│   └── diagnostic-bundle.schema.json
└── versioning/
    ├── compatibility-policy.md
    └── deprecated-interface-policy.md
```

# 9. Native desktop shell

``` text
desktop/
├── README.md
├── shell/
│   ├── app_main.*
│   ├── shell_application.*
│   ├── shell_controller.*
│   ├── shell_state.*
│   ├── shell_settings.*
│   ├── shell_startup.*
│   ├── shell_shutdown.*
│   ├── shell_error_page.*
│   └── CMakeLists.txt
├── compositor/
│   ├── compositor_adapter.*
│   ├── wayland_session.*
│   ├── xwayland_compatibility.*
│   ├── display_manager.*
│   ├── monitor_layout.*
│   ├── scaling_manager.*
│   └── compositor_policy.conf
├── window-manager/
│   ├── window_manager.*
│   ├── window_state.*
│   ├── window_focus.*
│   ├── z_order.*
│   ├── move_resize.*
│   ├── minimize_maximize.*
│   ├── tiling_layout.*
│   ├── virtual_desktops.*
│   └── window_capabilities.*
├── panels/
│   ├── top_bar/
│   │   ├── top_bar.*
│   │   ├── clock_widget.*
│   │   ├── system_status_widget.*
│   │   └── quick_settings.*
│   ├── taskbar/
│   │   ├── taskbar.*
│   │   ├── launcher_items.*
│   │   ├── active_app_indicator.*
│   │   └── taskbar_state.*
│   ├── notification_center/
│   │   ├── notification_center.*
│   │   └── notification_item.*
│   ├── activity_panel/
│   │   ├── activity_panel.*
│   │   └── activity_item.*
│   └── focus_chip/
│       ├── focus_chip.*
│       └── focus_state_view.*
├── desktop-icons/
│   ├── desktop_icon_view.*
│   ├── desktop_layout.*
│   └── desktop_entry_loader.*
├── launcher/
│   ├── app_launcher.*
│   ├── app_catalog.*
│   ├── recent_apps.*
│   ├── command_search.*
│   └── keyboard_navigation.*
├── windows/
│   ├── window_frame.*
│   ├── title_bar.*
│   ├── window_controls.*
│   ├── resize_handles.*
│   ├── drag_controller.*
│   └── window_menu.*
├── theme/
│   ├── palette.yaml
│   ├── typography.yaml
│   ├── spacing.yaml
│   ├── radii.yaml
│   ├── shadows.yaml
│   ├── motion.yaml
│   ├── icon-theme.yaml
│   └── widget-style.*
├── miso-view/
│   ├── miso_companion_view.*
│   ├── miso_panel.*
│   ├── miso_speech_bubble.*
│   ├── miso_status_indicator.*
│   ├── miso_busy_state.*
│   ├── miso_error_state.*
│   └── miso_accessible_description.*
├── focus-mode/
│   ├── focus_controller.*
│   ├── distraction_dimming.*
│   ├── focus_timer_view.*
│   └── focus_completion_view.*
├── dialogs/
│   ├── confirmation_dialog.*
│   ├── permission_dialog.*
│   ├── destructive_action_dialog.*
│   ├── file_picker_adapter.*
│   ├── error_dialog.*
│   └── about_aether_dialog.*
├── notifications/
│   ├── toast_manager.*
│   ├── toast_view.*
│   └── notification_actions.*
├── accessibility/
│   ├── accessible_tree.*
│   ├── screen_reader_bridge.*
│   ├── keyboard_focus.*
│   ├── high_contrast.*
│   ├── font_scaling.*
│   ├── reduced_motion.*
│   └── text_only_mode.*
├── assets/
│   ├── icons/
│   ├── wallpapers/
│   ├── fonts/
│   ├── miso/
│   │   ├── miso.svg
│   │   ├── miso-idle.svg
│   │   ├── miso-walk.svg
│   │   ├── miso-run.svg
│   │   ├── miso-jump.svg
│   │   ├── miso-sleep.svg
│   │   ├── miso-focus.svg
│   │   ├── miso-search.svg
│   │   └── miso-carry.svg
│   └── sounds/
├── session/
│   ├── session_entry.*
│   ├── session_environment.*
│   ├── session_restore.*
│   └── session_lock.*
├── settings-integration/
│   ├── settings_bridge.*
│   └── live_setting_state.*
└── CMakeLists.txt
```

Responsibilities: - `shell/` --- native desktop process and application
lifecycle, not a webpage. - `compositor/` and `window-manager/` --- real
Wayland session, window focus, stacking, resizing, virtual desktops and
multi-monitor layout. - `panels/` --- live status, launcher/taskbar,
notifications and activity backed by system APIs. - `theme/` and
`assets/miso/` --- supplied visual language and cat artwork/motion;
presentation never substitutes for a real backend action. -
`accessibility/` --- keyboard navigation, focus visibility,
screen-reader semantics, scaling, high contrast and reduced-motion
equivalents.

# 10. Built-in native applications

``` text
applications/
├── app-framework/
│   ├── app_main.*
│   ├── application_context.*
│   ├── app_lifecycle.*
│   ├── app_metadata.schema.json
│   ├── app_launcher_protocol.*
│   └── CMakeLists.txt
├── files/
│   ├── main.*
│   ├── files_window.*
│   ├── navigation_sidebar.*
│   ├── file_list_model.*
│   ├── file_operations.*
│   ├── file_permissions_view.*
│   ├── file_preview.*
│   ├── file_metadata_view.*
│   ├── intentfs_search_panel.*
│   ├── concept_chips.*
│   ├── trash_view.*
│   ├── archive_adapter.*
│   └── CMakeLists.txt
├── writer/
│   ├── main.*
│   ├── document_model.*
│   ├── editor_view.*
│   ├── document_storage.*
│   ├── autosave.*
│   ├── recovery_drafts.*
│   ├── file_chooser.*
│   ├── local_ai_assist.*
│   └── CMakeLists.txt
├── terminal/
│   ├── main.*
│   ├── terminal_window.*
│   ├── pty_session.*
│   ├── shell_process.*
│   ├── working_directory.*
│   ├── terminal_history.*
│   ├── copy_paste.*
│   ├── resize_handler.*
│   └── CMakeLists.txt
├── code/
│   ├── main.*
│   ├── editor_buffer.*
│   ├── syntax_highlighter.*
│   ├── project_folder.*
│   ├── find_replace.*
│   ├── file_save.*
│   ├── language_support.*
│   ├── local_code_assist.*
│   └── CMakeLists.txt
├── gallery/
│   ├── main.*
│   ├── image_browser.*
│   ├── thumbnail_cache.*
│   ├── image_decoder.*
│   ├── orientation_handler.*
│   ├── zoom_pan.*
│   └── CMakeLists.txt
├── calculator/
│   ├── main.*
│   ├── expression_parser.*
│   ├── arithmetic_engine.*
│   ├── history_model.*
│   └── CMakeLists.txt
├── clock/
│   ├── main.*
│   ├── clock_view.*
│   ├── timezone_view.*
│   ├── timer_view.*
│   ├── alarm_service_client.*
│   └── CMakeLists.txt
├── focus/
│   ├── main.*
│   ├── focus_session.*
│   ├── break_scheduler.*
│   ├── distraction_rules.*
│   ├── completion_notification.*
│   └── CMakeLists.txt
├── system-monitor/
│   ├── main.*
│   ├── process_table.*
│   ├── cpu_graph.*
│   ├── memory_graph.*
│   ├── storage_view.*
│   ├── network_view.*
│   ├── battery_thermal_view.*
│   ├── service_status_view.*
│   ├── process_action_policy.*
│   └── CMakeLists.txt
├── settings/
│   ├── main.*
│   ├── settings_shell.*
│   ├── appearance_page.*
│   ├── display_page.*
│   ├── audio_page.*
│   ├── network_page.*
│   ├── bluetooth_page.*
│   ├── keyboard_mouse_page.*
│   ├── power_page.*
│   ├── user_accounts_page.*
│   ├── privacy_page.*
│   ├── permissions_page.*
│   ├── accessibility_page.*
│   ├── ai_runtime_page.*
│   ├── intentfs_page.*
│   ├── updates_page.*
│   ├── backup_recovery_page.*
│   └── CMakeLists.txt
├── software-center/
│   ├── main.*
│   ├── repository_browser.*
│   ├── package_details.*
│   ├── dependency_view.*
│   ├── signature_status.*
│   ├── install_transaction.*
│   ├── uninstall_transaction.*
│   └── CMakeLists.txt
├── browser/
│   ├── package-policy.md
│   └── default-browser.desktop
├── screenshot/
│   ├── screenshot_service.*
│   ├── capture_region.*
│   ├── capture_window.*
│   └── save_dialog.*
├── archive-manager/
│   ├── archive_browser.*
│   ├── archive_extract.*
│   └── archive_create.*
├── backup-center/
│   ├── backup_dashboard.*
│   ├── backup_targets.*
│   ├── restore_wizard.*
│   └── backup_status.*
├── recovery-center/
│   ├── recovery_dashboard.*
│   ├── update_rollback_view.*
│   ├── model_repair_view.*
│   ├── intentfs_rebuild_view.*
│   └── diagnostic_export_view.*
└── mines/
    ├── main.*
    ├── game_state.*
    ├── game_logic.*
    └── accessible_controls.*
```

Each app needs a desktop entry, icon, localization domain, accessibility
labels, real persistence where applicable, error handling, and package
manifest. The browser is a normal maintained application/package, not
the host for the desktop shell.

# 11. Aether Runtime --- native local model platform

``` text
ai/
├── README.md
├── runtime/
│   ├── daemon/
│   │   ├── main.*
│   │   ├── runtime_service.*
│   │   ├── runtime_state.*
│   │   ├── runtime_config.*
│   │   ├── runtime_health.*
│   │   └── CMakeLists.txt
│   ├── api/
│   │   ├── inference_api.*
│   │   ├── request_router.*
│   │   ├── response_stream.*
│   │   ├── cancellation.*
│   │   └── api_version.*
│   ├── hardware-profile/
│   │   ├── profiler.*
│   │   ├── cpu_features.*
│   │   ├── ram_headroom.*
│   │   ├── gpu_probe.*
│   │   ├── npu_probe.*
│   │   ├── shared_memory_estimator.*
│   │   ├── storage_budget.*
│   │   ├── power_thermal_profile.*
│   │   └── profile.schema.json
│   ├── recommendation/
│   │   ├── recommendation_engine.*
│   │   ├── workload_classifier.*
│   │   ├── memory_estimator.*
│   │   ├── latency_estimator.*
│   │   ├── compatibility_filter.*
│   │   ├── priority_policy.*
│   │   └── recommendation.schema.json
│   ├── model-catalog/
│   │   ├── catalog_loader.*
│   │   ├── catalog_signature.*
│   │   ├── catalog_cache.*
│   │   ├── model_profile.schema.json
│   │   └── catalog-format.md
│   ├── model-manager/
│   │   ├── model_registry.*
│   │   ├── model_install.*
│   │   ├── model_remove.*
│   │   ├── model_pin.*
│   │   ├── model_version.*
│   │   ├── model_quota.*
│   │   ├── model_migration.*
│   │   └── installed-model.schema.json
│   ├── download/
│   │   ├── download_manager.*
│   │   ├── resumable_download.*
│   │   ├── download_queue.*
│   │   ├── cancellation.*
│   │   ├── disk_space_guard.*
│   │   ├── manifest_verifier.*
│   │   ├── digest_verifier.*
│   │   └── license_acceptance.*
│   ├── backend/
│   │   ├── backend_interface.*
│   │   ├── backend_registry.*
│   │   ├── backend_loader.*
│   │   ├── cpu_backend_adapter.*
│   │   ├── gpu_backend_adapter.*
│   │   ├── accelerator_backend_adapter.*
│   │   ├── llama_cpp_adapter.*
│   │   └── backend_capabilities.schema.json
│   ├── inference/
│   │   ├── inference_scheduler.*
│   │   ├── prompt_builder.*
│   │   ├── tokenizer_adapter.*
│   │   ├── context_manager.*
│   │   ├── kv_cache_budget.*
│   │   ├── streaming_decoder.*
│   │   ├── stop_conditions.*
│   │   ├── inference_timeout.*
│   │   └── output_validation.*
│   ├── queues/
│   │   ├── interactive_queue.*
│   │   ├── indexing_queue.*
│   │   ├── download_queue.*
│   │   ├── queue_limits.*
│   │   ├── backpressure.*
│   │   └── task_cancellation.*
│   ├── resource-governor/
│   │   ├── governor.*
│   │   ├── memory_pressure_handler.*
│   │   ├── unload_idle_model.*
│   │   ├── background_throttle.*
│   │   ├── battery_policy.*
│   │   ├── thermal_policy.*
│   │   └── resource_budget.schema.json
│   ├── validation/
│   │   ├── model_integrity.*
│   │   ├── safe_load_policy.*
│   │   ├── warmup.*
│   │   ├── inference_smoke_check.*
│   │   └── validation_report.schema.json
│   ├── privacy/
│   │   ├── local_endpoint_policy.*
│   │   ├── prompt_log_policy.*
│   │   ├── data_retention.*
│   │   └── remote_provider_consent.*
│   ├── persistence/
│   │   ├── runtime_database.*
│   │   ├── atomic_config_writer.*
│   │   └── migration_manager.*
│   └── CMakeLists.txt
├── firstboot/
│   ├── firstboot_controller.*
│   ├── welcome_page.*
│   ├── privacy_choices.*
│   ├── hardware_summary.*
│   ├── model_recommendation_page.*
│   ├── model_download_page.*
│   ├── model_validation_page.*
│   ├── no_model_mode.*
│   └── firstboot_state.schema.json
├── ui/
│   ├── runtime_settings_page.*
│   ├── model_catalog_view.*
│   ├── model_details_view.*
│   ├── download_progress_view.*
│   ├── model_health_view.*
│   ├── resource_usage_view.*
│   └── runtime_status_widget.*
├── catalog/
│   ├── catalog.schema.json
│   ├── README.md
│   └── sources-policy.yaml
├── policies/
│   ├── model-license-policy.yaml
│   ├── download-consent-policy.yaml
│   ├── resource-budget-policy.yaml
│   └── no-network-default.yaml
└── CMakeLists.txt
```

Runtime must distinguish measured facts from estimates, reject
incompatible models before downloading, show
license/source/size/storage/network details, verify hashes/signatures,
support cancel/resume/remove/rollback, validate a harmless inference,
and remain optional. No model installed or model crash must not prevent
login, file operations, networking, or ordinary applications.

# 12. IntentFS --- meaning-aware file indexing and search

``` text
intentfs/
├── README.md
├── daemon/
│   ├── main.*
│   ├── intentfs_service.*
│   ├── service_state.*
│   └── CMakeLists.txt
├── watcher/
│   ├── filesystem_watcher.*
│   ├── event_normalizer.*
│   ├── rename_move_tracker.*
│   ├── missed_event_reconciler.*
│   └── watch_scope_policy.*
├── pipeline/
│   ├── job_scheduler.*
│   ├── priority_queue.*
│   ├── low_resource_pause.*
│   ├── cancellation.*
│   └── pipeline_state.schema.json
├── extraction/
│   ├── extractor_interface.*
│   ├── plain_text_extractor.*
│   ├── markdown_extractor.*
│   ├── pdf_text_extractor.*
│   ├── office_document_extractor.*
│   ├── source_code_extractor.*
│   ├── filename_metadata_extractor.*
│   ├── image_metadata_extractor.*
│   ├── optional_ocr_adapter.*
│   ├── mime_detection.*
│   ├── file_size_limits.*
│   └── extraction_result.schema.json
├── concepts/
│   ├── concept_prompt.*
│   ├── concept_generator.*
│   ├── concept_normalizer.*
│   ├── concept_validator.*
│   ├── uniqueness_validator.*
│   ├── exactly_three_enforcer.*
│   ├── bounded_retry.*
│   └── concept_record.schema.json
├── index/
│   ├── metadata_store.*
│   ├── schema.sql
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   ├── stable_file_id.*
│   ├── content_fingerprint.*
│   ├── index_transaction.*
│   ├── tombstone_policy.*
│   └── rebuild_index.*
├── search/
│   ├── search_service.*
│   ├── filename_search.*
│   ├── path_search.*
│   ├── concept_search.*
│   ├── extracted_text_search.*
│   ├── optional_embedding_search.*
│   ├── ranking.*
│   ├── freshness_boost.*
│   ├── filters.*
│   ├── explain_match.*
│   └── search_result.schema.json
├── privacy/
│   ├── folder_exclusions.*
│   ├── sensitive_path_policy.*
│   ├── per_user_scope.*
│   ├── removable_drive_policy.*
│   ├── extracted_content_retention.*
│   ├── index_delete_only.*
│   └── privacy_settings.schema.json
├── api/
│   ├── query_api.*
│   ├── metadata_api.*
│   ├── reindex_api.*
│   ├── pause_resume_api.*
│   └── clear_index_api.*
├── ui/
│   ├── index_status.*
│   ├── concept_chip_view.*
│   ├── indexing_error_view.*
│   ├── exclusion_manager.*
│   └── search_reason_view.*
└── CMakeLists.txt
```

Core guarantees: - File operations remain available if IntentFS or the
model is offline. - Exact filename/path search does not wait for
inference. - Every successfully indexed supported file has exactly three
distinct concepts; malformed output is retried a bounded number of
times, then marked failed/pending. - Original file bytes are never
changed by indexing. Clearing the index never deletes source files. -
Respect file permissions, excluded folders, removable-media consent,
file-size limits, per-user boundaries and privacy settings. - Treat
extracted file text as untrusted input; it cannot change agent policies
or trigger capabilities.

# 13. Miso agent, CapabilityOS, broker and Action Ledger

``` text
miso/
├── README.md
├── agent/
│   ├── main.*
│   ├── agent_service.*
│   ├── conversation_state.*
│   ├── context_builder.*
│   ├── intent_classifier.*
│   ├── task_planner.*
│   ├── plan_decomposer.*
│   ├── capability_selector.*
│   ├── execution_orchestrator.*
│   ├── result_verifier.*
│   ├── response_composer.*
│   ├── task_cancellation.*
│   ├── task_budget.*
│   └── agent_task.schema.json
├── runtime-client/
│   ├── inference_client.*
│   ├── streaming_client.*
│   ├── runtime_status_client.*
│   └── local_only_policy.*
├── capability-os/
│   ├── registry/
│   │   ├── capability_registry.*
│   │   ├── registry_loader.*
│   │   ├── version_compatibility.*
│   │   └── capability.schema.json
│   ├── schemas/
│   │   ├── app.capabilities.json
│   │   ├── window.capabilities.json
│   │   ├── files.capabilities.json
│   │   ├── writer.capabilities.json
│   │   ├── focus.capabilities.json
│   │   ├── system-status.capabilities.json
│   │   ├── model.capabilities.json
│   │   ├── workspace.capabilities.json
│   │   └── settings.capabilities.json
│   ├── client/
│   │   ├── capability_client.*
│   │   └── capability_result.*
│   └── docs/
│       └── capability-authoring.md
├── broker/
│   ├── main.*
│   ├── broker_service.*
│   ├── request_authentication.*
│   ├── schema_validation.*
│   ├── identity_check.*
│   ├── permission_check.*
│   ├── resource_scope_check.*
│   ├── risk_classifier.*
│   ├── confirmation_policy.*
│   ├── rate_limiter.*
│   ├── idempotency_store.*
│   ├── execution_dispatcher.*
│   ├── timeout_and_cancellation.*
│   ├── result_verification.*
│   ├── rollback_dispatcher.*
│   └── broker_audit_hooks.*
├── policy-engine/
│   ├── policy_engine.*
│   ├── policy_loader.*
│   ├── policy_decision.*
│   ├── policy_version.*
│   ├── policy.schema.json
│   ├── default-policy.yaml
│   ├── read-only-policy.yaml
│   ├── reversible-action-policy.yaml
│   ├── write-action-policy.yaml
│   └── destructive-action-policy.yaml
├── capabilities/
│   ├── apps/
│   │   ├── list_apps.*
│   │   ├── open_app.*
│   │   ├── close_app.*
│   │   ├── focus_app.*
│   │   └── create_workspace.*
│   ├── windows/
│   │   ├── list_windows.*
│   │   ├── arrange_windows.*
│   │   ├── tile_windows.*
│   │   ├── minimize_window.*
│   │   └── restore_window.*
│   ├── files/
│   │   ├── search_files.*
│   │   ├── show_file_metadata.*
│   │   ├── open_file.*
│   │   ├── create_folder.*
│   │   ├── copy_file.*
│   │   ├── move_file.*
│   │   ├── rename_file.*
│   │   ├── move_to_trash.*
│   │   ├── restore_from_trash.*
│   │   └── index_file.*
│   ├── writer/
│   │   ├── create_document.*
│   │   ├── open_document.*
│   │   ├── save_draft.*
│   │   └── summarize_selected_document.*
│   ├── focus/
│   │   ├── start_focus_session.*
│   │   ├── pause_focus_session.*
│   │   ├── end_focus_session.*
│   │   └── start_break.*
│   ├── system/
│   │   ├── get_cpu_memory_status.*
│   │   ├── get_storage_status.*
│   │   ├── get_network_status.*
│   │   ├── get_battery_status.*
│   │   ├── get_service_status.*
│   │   └── read_selected_logs.*
│   ├── models/
│   │   ├── get_runtime_status.*
│   │   ├── list_models.*
│   │   ├── recommend_model.*
│   │   ├── start_download.*
│   │   ├── cancel_download.*
│   │   └── switch_model.*
│   ├── workspaces/
│   │   ├── save_workspace.*
│   │   ├── preview_workspace_restore.*
│   │   └── restore_workspace.*
│   └── settings/
│       ├── read_setting.*
│       └── change_setting.*
├── ledger/
│   ├── main.*
│   ├── ledger_service.*
│   ├── append_record.*
│   ├── query_history.*
│   ├── redact_secrets.*
│   ├── retention_policy.*
│   ├── clear_history.*
│   ├── recovery_link.*
│   ├── schema.sql
│   └── ledger_entry.schema.json
├── workspaces/
│   ├── workspace_service.*
│   ├── workspace_store.*
│   ├── context_resolver.*
│   ├── layout_capture.*
│   ├── restore_preview.*
│   ├── restore_executor.*
│   ├── workspace.schema.json
│   └── workspace_migrations/
├── presence/
│   ├── event_subscriber.*
│   ├── event_classifier.*
│   ├── notification_rules.*
│   ├── notification_rate_limit.*
│   └── observed_vs_inferred.*
├── safety/
│   ├── untrusted_content_boundary.*
│   ├── prompt_injection_filter.*
│   ├── no_shell_interpolation.*
│   ├── sensitive_data_filter.*
│   ├── bounded_loop_guard.*
│   └── policy_integrity_guard.*
├── ui/
│   ├── assistant_panel.*
│   ├── conversation_view.*
│   ├── plan_preview.*
│   ├── capability_confirmation.*
│   ├── action_progress.*
│   ├── result_summary.*
│   ├── action_history_view.*
│   ├── undo_action_view.*
│   └── miso_accessible_mode.*
└── CMakeLists.txt
```

Agent safety requirements: - Miso emits structured requests to
registered capabilities, not arbitrary shell scripts. - The broker is
the only supported route for AI-originated privileged actions. -
Read-only actions, reversible actions, writes/external effects and
destructive actions have distinct policies. - Show exact targets and
effects before consequential actions; obtain explicit confirmation when
required. - Verify system state after execution; record request, plan,
permission decision, confirmation, result, errors and rollback
availability. - Never log passwords, authentication tokens or
private-key material. Agent cannot modify its own policy, disable ledger
enforcement or erase protected audit history.

# 14. Security, permissions and privacy

``` text
security/
├── README.md
├── identity/
│   ├── service-users.yaml
│   ├── service-groups.yaml
│   ├── account-policy.yaml
│   └── session-boundaries.md
├── authorization/
│   ├── polkit/
│   │   ├── aether-system-actions.policy
│   │   ├── aether-package-actions.policy
│   │   ├── aether-storage-actions.policy
│   │   └── aether-account-actions.policy
│   ├── capability-permissions.yaml
│   └── permission-migration-policy.yaml
├── sandbox/
│   ├── agent-sandbox.conf
│   ├── runtime-sandbox.conf
│   ├── indexer-sandbox.conf
│   ├── application-sandbox-policy.yaml
│   └── syscall-restrictions.md
├── hardening/
│   ├── kernel-hardening.yaml
│   ├── service-hardening.yaml
│   ├── filesystem-permissions.yaml
│   ├── network-hardening.yaml
│   └── secure-defaults.yaml
├── cryptography/
│   ├── artifact-verification.*
│   ├── digest-verification.*
│   ├── certificate-policy.md
│   └── key-rotation-policy.md
├── secrets/
│   ├── secret-store-interface.*
│   ├── secret-redaction.*
│   └── secret-handling-policy.md
├── privacy/
│   ├── local-first-defaults.yaml
│   ├── telemetry-policy.yaml
│   ├── model-download-consent.yaml
│   ├── microphone-consent.yaml
│   ├── removable-drive-indexing.yaml
│   ├── data-retention.yaml
│   └── user-data-export-delete.md
├── audit/
│   ├── audit-policy.yaml
│   ├── protected-event-types.yaml
│   └── audit-integrity.*
└── threat-model/
    ├── assets.md
    ├── trust-boundaries.md
    ├── attack-surfaces.md
    ├── prompt-injection.md
    ├── malicious-model-artifacts.md
    └── risk-register.yaml
```

# 15. Networking, device support and hardware integration

``` text
networking/
├── README.md
├── connection-manager/
│   ├── connection_manager.*
│   ├── wifi_scan.*
│   ├── wifi_connect.*
│   ├── ethernet_status.*
│   ├── dns_configuration.*
│   ├── dhcp_client_policy.yaml
│   └── connection_profiles.schema.json
├── firewall/
│   ├── firewall_backend.*
│   ├── default_rules.yaml
│   └── user_rule_validation.*
├── vpn/
│   ├── vpn_provider_interface.*
│   └── vpn_status.*
├── network-diagnostics/
│   ├── connectivity_check.*
│   ├── dns_diagnostics.*
│   ├── route_diagnostics.*
│   └── redacted_report.*
└── policies/
    ├── ai_network_access.yaml
    └── per_capability_transfer.yaml

hardware/
├── README.md
├── discovery/
│   ├── cpu_discovery.*
│   ├── memory_discovery.*
│   ├── pci_discovery.*
│   ├── usb_discovery.*
│   ├── storage_discovery.*
│   ├── display_discovery.*
│   ├── audio_discovery.*
│   ├── input_discovery.*
│   ├── bluetooth_discovery.*
│   ├── camera_discovery.*
│   ├── printer_discovery.*
│   └── sensor_discovery.*
├── compatibility/
│   ├── device-matrix.schema.json
│   ├── known-devices.yaml
│   ├── unsupported-devices.yaml
│   └── firmware-requirements.yaml
├── firmware/
│   ├── firmware-catalog.yaml
│   ├── license-metadata.yaml
│   └── installation-notice.*
└── fallbacks/
    ├── software-rendering-policy.yaml
    ├── no-accelerator-policy.yaml
    └── missing-firmware-guidance.yaml
```

# 16. Installer and first-boot setup

``` text
installer/
├── README.md
├── app/
│   ├── main.*
│   ├── installer_controller.*
│   ├── installer_state.*
│   ├── installer_error.*
│   └── CMakeLists.txt
├── screens/
│   ├── welcome_screen.*
│   ├── language_keyboard_screen.*
│   ├── hardware_requirements_screen.*
│   ├── network_choice_screen.*
│   ├── target_disk_screen.*
│   ├── partition_plan_screen.*
│   ├── encryption_screen.*
│   ├── timezone_screen.*
│   ├── user_account_screen.*
│   ├── privacy_options_screen.*
│   ├── install_summary_screen.*
│   ├── install_progress_screen.*
│   ├── completion_screen.*
│   └── failure_recovery_screen.*
├── storage/
│   ├── disk_discovery.*
│   ├── partition_planner.*
│   ├── filesystem_creator.*
│   ├── encryption_setup.*
│   ├── mount_plan.*
│   ├── fstab_writer.*
│   └── destructive_action_guard.*
├── install/
│   ├── package_installer.*
│   ├── kernel_installer.*
│   ├── initramfs_installer.*
│   ├── bootloader_installer.*
│   ├── base_configurator.*
│   ├── user_creator.*
│   ├── desktop_configurator.*
│   ├── firstboot_configurator.*
│   └── install_transaction.*
├── logging/
│   ├── installer_log.*
│   ├── secret_filter.*
│   └── export_log.*
├── recovery/
│   ├── interrupted_install_recovery.*
│   └── install_rollback.*
└── schemas/
    ├── install-plan.schema.json
    └── install-report.schema.json

system/firstboot/
├── firstboot_wizard.*
├── locale_setup.*
├── keyboard_setup.*
├── timezone_setup.*
├── account_setup.*
├── network_setup.*
├── privacy_setup.*
├── disk_encryption_status.*
├── optional_ai_setup.*
├── model_recommendation.*
├── completion_state.*
└── firstboot.schema.json
```

The installer must explicitly name the selected target disk before
destructive changes, require confirmation, write a real installed
system, install the bootloader/kernel/initramfs/services/desktop, record
a redacted installation log, and not require network or model downloads
to complete installation.

# 17. Recovery, backup and rollback

``` text
recovery/
├── README.md
├── recovery-entry/
│   ├── recovery_main.*
│   ├── recovery_session.*
│   ├── system_detection.*
│   └── recovery_status.*
├── diagnostics/
│   ├── collect_system_state.*
│   ├── inspect_boot_state.*
│   ├── inspect_service_state.*
│   ├── inspect_disk_state.*
│   ├── inspect_update_state.*
│   └── redacted_bundle.*
├── repair/
│   ├── filesystem_repair_frontend.*
│   ├── package_database_repair.*
│   ├── bootloader_repair.*
│   ├── initramfs_rebuild.*
│   ├── user_config_repair.*
│   ├── runtime_config_reset.*
│   ├── model_remove_broken.*
│   └── intentfs_rebuild.*
├── rollback/
│   ├── known_good_boot_entry.*
│   ├── kernel_rollback.*
│   ├── system_snapshot_adapter.*
│   ├── package_rollback.*
│   └── rollback_manifest.schema.json
├── backup/
│   ├── backup_catalog.*
│   ├── backup_target_manager.*
│   ├── restore_catalog.*
│   ├── restore_preview.*
│   └── restore_transaction.*
└── ui/
    ├── recovery_menu.*
    ├── repair_summary.*
    ├── restore_wizard.*
    └── diagnostic_export_consent.*
```

Recovery tools must work without a network connection for core repair
tasks. Never claim a backup or snapshot exists unless it is configured
and verified.

# 18. Package manager, repositories and software updates

``` text
package-manager/
├── README.md
├── core/
│   ├── package_manager.*
│   ├── package_database.*
│   ├── dependency_solver.*
│   ├── transaction_engine.*
│   ├── install_package.*
│   ├── remove_package.*
│   ├── upgrade_package.*
│   ├── rollback_transaction.*
│   └── package_state.schema.json
├── format/
│   ├── package_manifest.schema.json
│   ├── file_manifest.schema.json
│   ├── dependency.schema.json
│   └── lifecycle-hooks-policy.md
├── repository/
│   ├── repository_config.schema.json
│   ├── repository_client.*
│   ├── metadata_verifier.*
│   ├── signature_verifier.*
│   ├── mirror_selector.*
│   └── trust_store_policy.yaml
├── ui/
│   ├── package_search.*
│   ├── package_details.*
│   ├── transaction_preview.*
│   └── package_history.*
└── policy/
    ├── trusted_sources.yaml
    ├── signature_required.yaml
    └── privileged_install_confirmation.yaml

updater/
├── README.md
├── daemon/
│   ├── main.*
│   ├── update_service.*
│   ├── update_scheduler.*
│   └── update_state.*
├── discovery/
│   ├── update_check.*
│   ├── release_channel.*
│   └── security_advisories.*
├── verification/
│   ├── metadata_signature.*
│   ├── package_digest.*
│   └── release_manifest.*
├── planning/
│   ├── update_plan.*
│   ├── disk_space_check.*
│   ├── compatibility_check.*
│   ├── migration_plan.*
│   └── reboot_requirement.*
├── apply/
│   ├── staged_update.*
│   ├── atomic_switch.*
│   ├── boot_entry_update.*
│   ├── post_update_health.*
│   └── rollback_trigger.*
├── model-updates/
│   ├── model_catalog_update.*
│   ├── model_version_pin.*
│   └── model_rollback.*
├── ui/
│   ├── update_dashboard.*
│   ├── changelog_view.*
│   ├── update_consent.*
│   ├── progress_view.*
│   └── rollback_view.*
└── schemas/
    ├── update-plan.schema.json
    └── update-result.schema.json
```

OS, kernel, desktop, AI runtime and model versions must be tracked
separately. Updates require trusted signed metadata, a visible change
summary, disk-space checks, failure handling and a known-good recovery
route.

# 19. Accessibility and localization

``` text
accessibility/
├── README.md
├── keyboard/
│   ├── global-shortcuts.yaml
│   ├── focus-order-policy.md
│   └── keyboard_navigation.*
├── screen-reader/
│   ├── accessible_role_map.yaml
│   ├── announcement_policy.yaml
│   └── screen_reader_adapter.*
├── visual/
│   ├── high-contrast-theme.yaml
│   ├── font-scaling.yaml
│   ├── display-scaling.yaml
│   └── focus-indicators.yaml
├── motion/
│   ├── reduced-motion.yaml
│   └── animation-intensity.yaml
├── voice/
│   ├── voice-consent.yaml
│   ├── microphone-indicator.*
│   └── text-fallback.*
└── audit/
    └── accessibility-requirements.md

localization/
├── README.md
├── locales/
│   ├── en/
│   │   ├── desktop.po
│   │   ├── installer.po
│   │   ├── applications.po
│   │   ├── runtime.po
│   │   └── miso.po
│   └── locale-template.pot
├── keyboard-layouts/
├── fonts/
├── date-number-formats/
└── localization-policy.md
```

# 20. Assets and visual design source

``` text
assets/
├── branding/
│   ├── aether-logo.svg
│   ├── aether-mark.svg
│   ├── wordmark.svg
│   └── brand-guidelines.md
├── desktop/
│   ├── wallpaper-default.png
│   ├── palette.yaml
│   ├── typography.yaml
│   └── spacing.yaml
├── icons/
│   ├── apps/
│   ├── devices/
│   ├── status/
│   └── actions/
├── miso/
│   ├── miso.svg
│   ├── idle/
│   ├── walk/
│   ├── run/
│   ├── jump/
│   ├── sleep/
│   ├── focus/
│   ├── search/
│   ├── carry/
│   └── accessibility/
├── sounds/
└── fonts/
```

Preserve supplied artwork where licensing allows, but integrate it into
the native shell. The HTML reference is a design/behavior source only
and is not shipped as the desktop itself.

# 21. Data, migrations and runtime state schemas

``` text
data/
├── schemas/
│   ├── user-settings.schema.json
│   ├── system-settings.schema.json
│   ├── hardware-profile.schema.json
│   ├── model-profile.schema.json
│   ├── intentfs-record.schema.json
│   ├── capability.schema.json
│   ├── action-ledger-entry.schema.json
│   ├── workspace.schema.json
│   ├── notification.schema.json
│   ├── package-state.schema.json
│   ├── update-state.schema.json
│   └── diagnostic-bundle.schema.json
├── migrations/
│   ├── README.md
│   ├── system/
│   ├── user/
│   ├── intentfs/
│   ├── ledger/
│   └── workspace/
├── defaults/
│   ├── system-settings.yaml
│   ├── privacy-settings.yaml
│   ├── accessibility-settings.yaml
│   ├── runtime-settings.yaml
│   ├── intentfs-settings.yaml
│   └── shell-settings.yaml
└── policies/
    ├── retention.yaml
    ├── export.yaml
    └── deletion.yaml
```

Actual mutable databases belong in the installed system's
`/var/lib/aether/` or user-local data directory, not in source control.
Schema migrations must be versioned, transactional where feasible, and
recoverable after interruption.

# 22. Firmware and third-party source management

``` text
firmware/
├── README.md
├── manifest.yaml
├── license-review/
│   └── redistribution-matrix.csv
└── fetch-policy.md

third-party/
├── README.md
├── source-lock.yaml
├── licenses/
├── patches/
├── inference-backends/
│   ├── README.md
│   └── backend-license-review.md
├── desktop-dependencies/
└── sbom/
```

-   Pin each third-party source to an immutable version/commit and
    record its license and security status.
-   Do not bundle model weights unless their license and redistribution
    terms permit it.
-   Firmware may require separate acquisition or notices; report missing
    firmware accurately.
-   Do not commit credentials, production signing keys, private user
    data, downloaded model weights, build outputs, or unexplained binary
    blobs.

# 23. Packaging source layout

``` text
packaging/
├── base/
│   ├── aether-base.package
│   ├── aether-init.package
│   ├── aether-session.package
│   ├── aether-hardware.package
│   ├── aether-networking.package
│   ├── aether-security-policy.package
│   └── aether-logging.package
├── kernel/
│   ├── linux-aether.package
│   ├── linux-aether-modules.package
│   ├── linux-aether-firmware.package
│   └── kernel-install-hooks.*
├── desktop/
│   ├── aether-shell.package
│   ├── aether-theme.package
│   ├── aether-icons.package
│   ├── aether-session.package
│   └── aether-accessibility.package
├── applications/
│   ├── aether-files.package
│   ├── aether-writer.package
│   ├── aether-terminal.package
│   ├── aether-code.package
│   ├── aether-gallery.package
│   ├── aether-settings.package
│   ├── aether-system-monitor.package
│   ├── aether-software-center.package
│   └── aether-recovery-center.package
├── ai/
│   ├── aether-runtime.package
│   ├── aether-runtime-backend-llamacpp.package
│   ├── aether-intentfs.package
│   ├── aether-miso.package
│   ├── aether-capability-broker.package
│   └── aether-action-ledger.package
├── installer/
│   ├── aether-installer.package
│   └── aether-firstboot.package
├── recovery/
│   └── aether-recovery.package
├── updater/
│   ├── aether-package-manager.package
│   └── aether-updater.package
└── manifests/
    ├── base.yaml
    ├── desktop.yaml
    ├── installer.yaml
    ├── recovery.yaml
    └── optional-ai.yaml
```

The exact package file format depends on the selected base
distribution/package manager. These names describe package boundaries
and contents, not a demand to invent a package format unnecessarily.

# 24. Release and ISO output structure

Generated by the build system; do not hand-edit release artifacts.

``` text
artifacts/
├── packages/
│   ├── base/
│   ├── kernel/
│   ├── desktop/
│   ├── applications/
│   ├── ai/
│   ├── installer/
│   └── recovery/
├── kernel/
│   ├── vmlinuz
│   ├── System.map
│   ├── config
│   └── modules/
├── initramfs/
│   ├── initramfs-normal.img
│   ├── initramfs-installer.img
│   └── initramfs-recovery.img
├── rootfs/
│   ├── live/
│   ├── installer/
│   └── recovery/
├── iso-staging/
│   ├── boot/
│   │   ├── grub/
│   │   ├── vmlinuz
│   │   └── initramfs.img
│   ├── aether/
│   │   ├── live-root.squashfs
│   │   ├── package-repository/
│   │   └── release-manifest.json
│   └── EFI/
│       └── BOOT/
├── AetherOS-<version>-x86_64.iso
├── AetherOS-<version>-x86_64.iso.sha256
├── AetherOS-<version>-x86_64.iso.sig
├── SBOM.spdx.json
├── source-manifest.json
├── build-provenance.json
└── release-notes.md
```

The final release is a bootable ISO with a real bootloader, kernel,
initramfs and live system, plus an installer capable of deploying Aether
to disk. ISO generation must fail if required boot files, rootfs
components, manifests or signatures/checksums required by the release
policy are missing.

# 25. Build configuration and reproducible delivery

``` text
configs/
├── distro.yaml
├── architecture.yaml
├── boot-modes.yaml
├── kernel.yaml
├── initramfs.yaml
├── desktop.yaml
├── package-sources.yaml
├── repository-signing.yaml
├── firmware.yaml
├── default-applications.yaml
├── ai-defaults.yaml
├── privacy-defaults.yaml
├── accessibility-defaults.yaml
├── update-policy.yaml
└── release-policy.yaml
```

Each release build records the exact source revisions, kernel config
hash, patch list, compiler/toolchain versions, package versions,
firmware provenance, model catalog metadata version and build command.
Never describe an ISO as final merely because an ISO file was generated;
the installed OS must contain working core services and honest status
reporting.

# 26. Project-level implementation gates

These are delivery requirements, not a request to add a separate
test-only or emulator-only project tree.

1.  **Boot and installation:** ISO boots on the declared supported
    hardware; installer installs a real system; bootloader, kernel,
    initramfs and root filesystem are valid.
2.  **Core OS:** login, users, permissions, storage, networking,
    display, input, audio, service management, logs and power controls
    operate through real system services.
3.  **Native desktop:** shell starts after login, manages windows and
    panels, persists settings, supports keyboard access and reflects
    actual system state.
4.  **Applications:** Files and Terminal operate on the real filesystem
    and PTY; Writer saves real documents; Settings changes real
    supported settings; System Monitor reads actual telemetry.
5.  **Runtime:** hardware profiling uses real interfaces; recommendation
    explains limits; download requires consent; artifact integrity is
    checked; model is actually loaded and inference verified; no-model
    mode works.
6.  **IntentFS:** file events reconcile correctly; indexing stays local;
    each successful record has exactly three distinct concepts; search
    explains why each result matched; index failure never blocks
    ordinary file access.
7.  **Miso and broker:** registered capability schemas, permissions,
    previews, confirmations, cancellation, result verification, ledger
    records and feasible undo are implemented.
8.  **Security and privacy:** AI agent runs unprivileged; privileged
    operations are brokered; no silent remote upload; secrets are
    redacted; model output is never directly executed as shell code.
9.  **Recovery and updates:** signed update metadata, visible changelog,
    rollback/known-good boot, model repair, IntentFS rebuild and offline
    recovery path are implemented.
10. **Release integrity:** source locks, licenses, SBOM, provenance,
    checksums and release notes accompany the ISO.

# 27. Explicitly out of scope for the source tree

-   No browser-based desktop as the OS.
-   No `index.html` or web server acting as the booted desktop.
-   No fake kernel source assembled from directory names.
-   No LLM in kernel mode or kernel-critical execution path.
-   No mandatory Ollama dependency or mandatory cloud AI/account.
-   No hard-coded demo files, simulated terminal, fake CPU/RAM values or
    fabricated successful action results.
-   No model download during installation that blocks bootability or
    core OS setup.
-   No unreviewed kernel fork full of speculative changes.
-   No test-only, QEMU-only or emulator-only product architecture. The
    ISO targets real supported hardware; any optional developer
    validation infrastructure is separate from the shipped OS.
-   No claims that the full OS has already been implemented merely
    because this directory structure has been specified.

## Final architectural statement

Aether is a complete Linux-based operating system distribution. Its
identity comes from its maintained kernel configuration and carefully
scoped patches, its own boot/install/recovery and release pipeline, real
system services, native desktop and applications, Aether Runtime,
IntentFS, Miso/CapabilityOS, and its security and privacy model. The
directory tree is the implementation blueprint; each listed component
must be implemented and integrated before the project can honestly be
called a finished OS.
