# AETHER OS --- `procedure.md`

## Final implementation directive and file-by-file engineering specification

**Product:** Aether Cognitive Operating System\
**Deliverable:** a standalone, independently bootable operating system
distributed as a real ISO image and installable to physical storage.\
**Project state required from the implementer:** final, integrated
implementation.\
**Primary references:** the approved Aether final folder structure and
*Aether_Full_Project_Description.docx*, including its subsystem
inventory, Runtime, IntentFS, Miso/CapabilityOS, native desktop,
security, installation, recovery, accessibility, data model, user
journeys and acceptance requirements.

------------------------------------------------------------------------

# 1. Binding instruction --- read before writing code

Build Aether as a complete, independently bootable Linux-based operating
system distribution. It must boot through a real
firmware/bootloader/kernel/initramfs chain, mount a real root
filesystem, start real system services, provide a real login/session and
native desktop, and be deliverable as an ISO that can be written to
removable media and booted on supported physical hardware.

This is **not** a website, web desktop, browser simulation, Electron
page presented as an OS, theme, Linux application bundle, container
image, subsystem, add-on OS, or visual prototype. The supplied
`aether-ui.html` is a design and interaction reference only. Recreate
its approved visual language and interactions in the actual native
desktop shell. Do not use the browser page as the operating system.

Treat the approved folder structure and project idea document as the
product contract. First evaluate every directory and component in that
structure, map it to the architecture in the project idea document,
resolve overlapping responsibilities, and then implement the integrated
product. Keep the agreed structure and naming unless a specific
technical conflict requires a documented, minimal change. Do not omit
components silently.

## Mandatory delivery rules

1.  **Final product, not a prototype.** Implement each included feature
    end-to-end and connect its UI to the real service, filesystem,
    kernel interface, or package manager that owns it.
2.  **No hard-coded behavior.** No fake file lists, fabricated CPU/RAM
    readings, canned AI answers presented as inference, fixed success
    messages, simulated downloads, placeholder buttons, invented action
    history, sample-only databases, or static model recommendations.
3.  **No deferred work.** Do not leave TODOs, FIXME markers, empty
    functions, stubs, mock implementations, "implement later" comments,
    placeholder screens, temporary workarounds, or a list of future
    fixes for required functionality. Resolve implementation issues
    within this delivery.
4.  **No scope deviation.** Do not replace Aether with a simpler
    product, remove difficult features, convert it into a web
    application, or quietly downgrade requirements. If a capability is
    genuinely unsupported by the selected hardware or upstream stack,
    report that limitation accurately and provide the required graceful
    fallback. Never pretend the unsupported capability works.
5.  **No arbitrary truncation because the project is large.** The size
    and complexity of the project are not permission to stop at a
    scaffold, generate only a subset, or deliver an architecture
    document instead of the product. Work through the complete
    dependency graph and all required components until the full agreed
    scope is implemented.
6.  **No false completion claims.** Do not say the OS is complete,
    bootable, installed, or operational merely because source files or
    an ISO filename exist. Release status must be based on the actual
    artifacts and the documented acceptance gates in this procedure.
7.  **No unreviewed kernel rewrite.** Use a pinned, maintained upstream
    Linux kernel and its real source tree. Aether's kernel identity
    comes from its configuration, build process, explicit justified
    patches, release policy and user-space integration. Do not recreate
    Linux from directory names.
8.  **AI belongs in user space.** Do not put LLM inference or agent
    planning into scheduler, interrupt, memory allocator,
    filesystem-critical or other kernel-critical paths. Core OS
    operation must not depend on a running model.
9.  **Local-first by default.** Core OS use must not require a cloud
    account, remote AI provider, or mandatory Ollama installation.
    Network use by AI capabilities must be explicit, purpose-limited and
    consented to.
10. **Every control must be real.** Every visible control must invoke a
    real operation and show its actual state/result, or be disabled with
    a clear reason. Do not make a control appear functional when its
    backend is absent.
11. **Use real platform APIs.** Prefer stable Linux interfaces and
    maintained upstream components for device drivers, networking,
    audio, graphics, filesystems, authentication and package handling.
    Do not implement custom replacements without a documented reason.
12. **Deliver a complete source tree and release artifacts.** Include
    source, configuration, package definitions, installer, recovery,
    documentation, provenance, license notices, software bill of
    materials, checksums and the bootable ISO as applicable to the
    chosen release method.

These rules are binding throughout the project. Do not interpret "very
large" as permission to split the product into a prototype now and
promised features later. Internal engineering may be organized into
coherent workstreams, but the final delivery must contain the whole
agreed product and must not deviate from this specification.

------------------------------------------------------------------------

# 2. Product definition and architecture decisions

Aether is a local-first, AI-native desktop OS. Its core differentiators
are:

-   A real Linux-based operating system and native desktop shell.
-   Aether Runtime: hardware-aware local-model discovery,
    recommendation, download, integrity verification, backend setup,
    inference verification, model lifecycle and resource governance.
-   IntentFS: OS-wide semantic file discovery with stable file identity,
    metadata, supported content extraction, and exactly three distinct
    model-predicted concepts per successfully indexed supported file.
-   Miso: a user-space agent that turns user intent into structured
    plans and invokes registered capabilities through the Capability
    Broker.
-   CapabilityOS: typed, versioned, permission-controlled system actions
    rather than arbitrary model-generated shell commands.
-   Action Ledger: visible, privacy-aware, append-oriented records of
    agent requests, plans, permissions, execution results and recovery
    options where feasible.
-   Living Workspaces: user-approved project context, related files,
    app/window layout, notes and restorable state, with a preview before
    changes are applied.
-   A warm native desktop based on the supplied visual reference,
    including the Miso companion, taskbar, panels, window chrome, focus
    mode, toasts and settings.
-   A complete installer, first-boot setup, update mechanism, recovery
    environment, accessibility support and documented hardware
    boundaries.

## Architecture boundary

**Kernel and trusted base:** upstream Linux kernel, boot chain,
init/service manager, account/session management, filesystem and device
APIs, core networking, graphics/audio stack, privilege enforcement and
essential system services.

**Unprivileged user-space AI:** Aether Runtime, inference backends,
IntentFS extraction/indexing, Miso planning, workspace suggestions and
AI-assisted explanations.

**Privileged action boundary:** the Capability Broker and narrowly
scoped system helpers. Miso and the model never receive unrestricted
root access. They cannot alter their own policies, grant themselves
permissions, disable audit enforcement, or execute arbitrary generated
shell strings.

## Core behavior when AI is unavailable

The machine must still boot, log in, launch apps, access files, use the
terminal, manage networking, adjust settings, install or remove
supported software, update and recover. Model download failure,
inference failure, low memory, unavailable acceleration, or an empty
model catalog must not break ordinary OS functionality. AI features
should display the true reason they are unavailable and provide
supported fallback behavior.

------------------------------------------------------------------------

# 3. Implementation order and dependency rules

Implement and integrate the components in dependency order. This order
controls technical dependencies; it does not authorize omitting later
components from the final delivery.

1.  **Source and release foundation:** pin the distribution base,
    upstream kernel, compiler/toolchain, bootloader, init system,
    graphics stack, package format and third-party dependencies. Record
    license and provenance.
2.  **Bootable base:** kernel configuration/build, bootloader entries,
    initramfs, root filesystem, device discovery, init/service manager,
    logging and shutdown.
3.  **Core operating system:** accounts, authentication, storage,
    filesystems, networking, audio, display/input, power management,
    package management, security policy and service health.
4.  **Native graphical session:** compositor/session, native shell,
    window management, panels, taskbar, launcher, notifications, theme,
    accessibility and settings.
5.  **Native applications:** Files, Terminal, Writer, Code, Gallery,
    Calculator, Clock, Focus, System Monitor, Software Center, Archive
    Manager, Screenshot, Backup Center and Recovery Center as specified
    in the folder structure.
6.  **Aether Runtime:** real hardware inventory, workload profiles,
    model catalog and licensing, recommendation, download, integrity
    checks, backend lifecycle, inference API, resource governance and
    first-boot UI.
7.  **IntentFS:** filesystem event tracking, extraction pipeline,
    concept generation/validation, metadata persistence, search API,
    privacy exclusions and native Files integration.
8.  **CapabilityOS and Miso:** capability schemas/registry, broker,
    policy engine, agent planner/executor, Action Ledger, Miso UI,
    presence events, workspaces, confirmations, cancellation and
    recovery.
9.  **Installer and first boot:** partition planning, optional
    encryption, account creation, OS installation, bootloader setup,
    first-boot wizard and optional model installation.
10. **Updates and recovery:** signed metadata, package transactions,
    system update strategy, rollback/known-good boot, recovery
    media/environment, backup/restore and repair tools.
11. **Release assembly:** rootfs, initramfs, bootloader, package
    repository/metadata, ISO, release manifest, licenses, SBOM,
    checksums, signatures and user documentation.

Do not hard-wire unrelated components together. Use the documented D-Bus
or equivalent local IPC contracts, versioned schemas, explicit ownership
and least-privilege service identities. Every service must have clear
startup dependencies, bounded timeouts, cancellation, health state,
structured logs and shutdown behavior.

------------------------------------------------------------------------

# 4. File-by-file implementation map

The approved folder tree is the authoritative source of paths. For every
path below, the required filename notation is:

`foldername-.subfoldername->...filename — what that file must do`

Each listed file is an implementation responsibility, not an empty
placeholder. Where the approved structure groups many source files under
a directory, implement all of them as defined by the folder tree and
this map. Use the repository's chosen language extension consistently
(`.c`, `.h`, `.cpp`, `.hpp`, `.rs`, `.py`, `.qml`, `.ui`, or another
justified native format); do not create multiple empty files merely to
match names.

## 4.1 Repository root and project governance

-   `AetherOS->README.md` --- describe the actual system, supported
    platform, source build, installation and release workflow; do not
    claim features that are not present.
-   `AetherOS->LICENSES.md` --- list project and bundled component
    licensing obligations.
-   `AetherOS->NOTICE` --- retain third-party attribution and required
    notices.
-   `AetherOS->SECURITY.md` --- define vulnerability reporting,
    supported release policy and security response.
-   `AetherOS->VERSION` --- define the authoritative OS release version.
-   `AetherOS->CHANGELOG.md` --- record user-visible changes and
    compatibility notes for each release.
-   `AetherOS->Makefile` / `AetherOS->justfile` --- provide stable,
    documented commands for source acquisition, package builds, rootfs
    assembly, ISO production and release metadata.
-   `AetherOS->.gitignore` --- exclude generated artifacts, local
    secrets, model weights and machine-specific state.
-   `AetherOS->.gitmodules` --- pin any submodule source revisions;
    never rely on a moving branch for release builds.
-   `AetherOS->docs->architecture->system-overview.md` --- explain the
    system layers, ownership and service boundaries.
-   `AetherOS->docs->architecture->kernel-boundary.md` --- specify what
    belongs in kernel space versus user space.
-   `AetherOS->docs->architecture->data-flow.md` --- document data
    movement among desktop, Runtime, IntentFS, Miso and system services.
-   `AetherOS->docs->architecture->failure-domains.md` --- specify what
    happens when each service fails and how ordinary OS use remains
    available.
-   `AetherOS->docs->decisions->ADR-0001-linux-kernel.md` --- record the
    selected upstream kernel and rationale.
-   `AetherOS->docs->decisions->ADR-0002-native-desktop-stack.md` ---
    record native compositor, toolkit and session choices.
-   `AetherOS->docs->decisions->ADR-0003-init-system.md` --- record
    init/service-manager choice and operational policy.
-   `AetherOS->docs->decisions->ADR-0004-package-format.md` --- record
    package format, repository trust and rollback strategy.
-   `AetherOS->docs->decisions->ADR-0005-inference-backend.md` ---
    record backend selection, supported model formats, license
    constraints and extension interface.
-   `AetherOS->docs->decisions->ADR-0006-system-update-strategy.md` ---
    define how OS updates are staged, committed and rolled back.

## 4.2 Linux kernel and platform

-   `AetherOS->kernel->upstream.lock` --- pin the exact upstream kernel
    version, commit, source location and verification data.
-   `AetherOS->kernel->configs->aether_defconfig` --- define the Aether
    kernel configuration for the declared architecture.
-   `AetherOS->kernel->configs->fragments->cpu-and-scheduler.config` ---
    configure supported CPU, scheduler and preemption facilities.
-   `AetherOS->kernel->configs->fragments->memory-and-cgroups.config`
    --- enable memory management, accounting, cgroups and required
    pressure reporting.
-   `AetherOS->kernel->configs->fragments->storage-and-filesystems.config`
    --- enable supported storage controllers, partition formats and
    filesystems.
-   `AetherOS->kernel->configs->fragments->networking.config` --- enable
    the supported network stack and required filtering/isolation
    facilities.
-   `AetherOS->kernel->configs->fragments->graphics-drm.config` ---
    configure DRM/KMS and graphics-driver support required by the target
    hardware.
-   `AetherOS->kernel->configs->fragments->input-and-hid.config` ---
    support keyboards, pointing devices, touchpads and HID hardware.
-   `AetherOS->kernel->configs->fragments->audio.config` --- enable
    required kernel sound interfaces.
-   `AetherOS->kernel->configs->fragments->security-and-lsm.config` ---
    enable the selected security modules and hardening options.
-   `AetherOS->kernel->configs->fragments->namespaces-and-seccomp.config`
    --- enable process isolation required by sandboxed services.
-   `AetherOS->kernel->configs->fragments->power-thermal.config` ---
    enable supported power, battery and thermal interfaces.
-   `AetherOS->kernel->patches->series` --- list only reviewed Aether
    patches in deterministic application order.
-   `AetherOS->kernel->patches->README.md` --- justify each patch,
    upstream status, security impact and removal path.
-   `AetherOS->kernel->scripts->fetch-upstream.sh` --- fetch the pinned
    source and verify its origin.
-   `AetherOS->kernel->scripts->verify-upstream.sh` --- verify source
    identity and integrity before building.
-   `AetherOS->kernel->scripts->apply-patches.sh` --- apply the declared
    patch series and fail on any mismatch.
-   `AetherOS->kernel->scripts->merge-config.sh` --- merge approved
    configuration fragments and reject invalid options.
-   `AetherOS->kernel->scripts->build-kernel.sh` --- build the actual
    upstream kernel for the declared architecture.
-   `AetherOS->kernel->scripts->collect-provenance.sh` --- record source
    revision, patch list, config hash and toolchain versions.
-   `AetherOS->kernel->provenance->upstream-commit.txt` --- record the
    exact upstream revision used for the build.
-   `AetherOS->kernel->provenance->patch-manifest.json` --- identify
    every applied patch and its digest.
-   `AetherOS->kernel->provenance->config-hash.txt` --- identify the
    exact kernel configuration used.
-   `AetherOS->kernel->provenance->toolchain-manifest.json` --- record
    compiler, linker and build tool versions.

**Kernel directory rule:** `kernel/source/linux/` must contain the real,
pinned upstream Linux source tree, including its own directories such as
`arch/`, `drivers/`, `fs/`, `include/`, `init/`, `ipc/`, `kernel/`,
`mm/`, `net/`, `security/`, `sound/`, `tools/` and `virt/`. Do not
generate substitute files or copy directory names without real source.
Do not put LLM inference into kernel mode.

## 4.3 Boot, initramfs and ISO build

-   `AetherOS->boot->grub->grub.cfg.in` --- generate normal, installer
    and recovery boot entries with correct kernel/initramfs paths and
    safe parameters.
-   `AetherOS->boot->grub->theme->theme.txt` --- provide a usable
    boot-menu theme without affecting boot reliability.
-   `AetherOS->boot->initramfs->init` --- discover the boot device, load
    essential modules, unlock configured encrypted storage, mount the
    root filesystem and switch to it.
-   `AetherOS->boot->initramfs->storage-discovery.conf` --- define
    reliable root-device discovery.
-   `AetherOS->boot->initramfs->cryptsetup.conf` --- configure
    encrypted-root unlocking when encryption is enabled.
-   `AetherOS->boot->initramfs->root-mount.conf` --- specify root
    filesystem identification and mount behavior.
-   `AetherOS->boot->initramfs->switch-root.conf` --- define the
    transition from initramfs to the installed/live root.
-   `AetherOS->boot->initramfs->hooks->10-device-discovery` --- discover
    required boot devices.
-   `AetherOS->boot->initramfs->hooks->20-storage-drivers` --- load the
    drivers needed to access the root device.
-   `AetherOS->boot->initramfs->hooks->30-filesystem-drivers` --- load
    required filesystem modules.
-   `AetherOS->boot->initramfs->hooks->40-encryption` --- unlock the
    encrypted root when configured.
-   `AetherOS->boot->initramfs->hooks->50-root-selection` --- resolve
    the configured root filesystem and validate it.
-   `AetherOS->boot->initramfs->hooks->90-switch-root` --- mount and
    transition to the real root.
-   `AetherOS->toolchain->versions.lock` --- pin the build toolchain
    versions.
-   `AetherOS->toolchain->host-prerequisites.md` --- list required host
    packages, disk space and build dependencies.
-   `AetherOS->toolchain->scripts->verify-toolchain.sh` --- verify
    required tools and versions before building.
-   `AetherOS->toolchain->scripts->verify-reproducibility.sh` --- check
    that the declared build inputs and environment are reproducible.
-   `AetherOS->build->profiles->desktop-x86_64.yaml` --- define the
    installed desktop image composition for x86-64.
-   `AetherOS->build->profiles->installer-x86_64.yaml` --- define the
    installer environment composition.
-   `AetherOS->build->profiles->recovery-x86_64.yaml` --- define the
    recovery environment composition.
-   `AetherOS->build->manifests->base-packages.yaml` --- list all
    packages required for boot and ordinary OS use.
-   `AetherOS->build->manifests->desktop-packages.yaml` --- list the
    complete native graphical session and desktop applications.
-   `AetherOS->build->manifests->ai-packages.yaml` --- list Runtime,
    IntentFS, Miso, broker and AI-facing integrations.
-   `AetherOS->build->manifests->firmware-packages.yaml` --- list
    redistributable firmware and its license/provenance.
-   `AetherOS->build->scripts->00-check-host.sh` --- verify build
    prerequisites and available space.
-   `AetherOS->build->scripts->10-fetch-sources.sh` --- retrieve all
    pinned sources and verify them.
-   `AetherOS->build->scripts->20-build-kernel.sh` --- build the
    configured kernel and modules.
-   `AetherOS->build->scripts->30-build-packages.sh` --- build or
    assemble all declared OS packages.
-   `AetherOS->build->scripts->40-assemble-rootfs.sh` --- assemble the
    real filesystem hierarchy, package payloads, configuration and
    permissions.
-   `AetherOS->build->scripts->50-build-initramfs.sh` --- produce the
    required initramfs images.
-   `AetherOS->build->scripts->60-stage-bootloader.sh` --- stage the
    selected bootloader and entries.
-   `AetherOS->build->scripts->70-build-live-environment.sh` ---
    assemble the bootable live OS root.
-   `AetherOS->build->scripts->80-build-installer-image.sh` --- assemble
    the installer environment.
-   `AetherOS->build->scripts->90-create-iso.sh` --- produce the actual
    bootable ISO from built artifacts.
-   `AetherOS->build->scripts->95-generate-checksums.sh` --- generate
    checksums for the release artifacts.
-   `AetherOS->build->scripts->99-create-release-manifest.sh` ---
    generate a manifest describing the exact contents and provenance of
    the release.
-   `AetherOS->build->iso->iso-layout.yaml` --- define the ISO directory
    and boot catalog layout.
-   `AetherOS->build->reproducibility->environment.lock` --- record the
    build environment.
-   `AetherOS->build->reproducibility->source-hashes.txt` --- record
    source digests used in the build.
-   `AetherOS->release->release-manifest.schema.json` --- define the
    schema for release artifact metadata.
-   `AetherOS->release->signing-policy.md` --- define release-signing
    procedure and private-key protection.

The final ISO must contain a real bootloader, kernel, initramfs, live
root filesystem, required drivers and system services, native desktop
and installer/recovery entry points. The ISO build must fail rather than
silently omit a required component. Support UEFI as the preferred modern
path; document any legacy firmware limitation and do not claim support
that is not delivered.

## 4.4 Root filesystem and base OS services

-   `AetherOS->rootfs->etc->os-release` --- expose correct Aether
    distribution identity and version.
-   `AetherOS->rootfs->etc->aether->system.yaml` --- define system-wide
    Aether service endpoints and defaults.
-   `AetherOS->rootfs->etc->aether->first-boot.yaml` --- persist
    first-boot setup state and resumable progress.
-   `AetherOS->rootfs->etc->aether->privacy-defaults.yaml` --- define
    local-first data and network defaults.
-   `AetherOS->rootfs->etc->aether->runtime.yaml` --- configure Runtime
    paths, resource policies and backend discovery.
-   `AetherOS->rootfs->etc->aether->intentfs.yaml` --- configure
    indexing scope, excluded paths, limits and database location.
-   `AetherOS->rootfs->etc->aether->miso.yaml` --- configure the agent
    service without embedding secrets or permissive policies.
-   `AetherOS->rootfs->etc->aether->capability-policy.yaml` --- define
    the default capability authorization policy.
-   `AetherOS->rootfs->etc->aether->update-policy.yaml` --- configure
    signed update sources and update behavior.
-   `AetherOS->system->init->service-manager-policy.conf` --- set
    dependency, restart, sandbox and resource-limit policy for system
    services.
-   `AetherOS->system->init->dependency-graph.yaml` --- declare startup
    dependencies and avoid circular service dependencies.
-   `AetherOS->system->init->shutdown-order.yaml` --- define safe
    shutdown and persistence ordering.
-   `AetherOS->system->services->aether-firstboot.service` --- launch
    and resume the first-boot wizard exactly when required.
-   `AetherOS->system->services->aether-hardware-probe.service` ---
    collect real hardware facts from supported system interfaces.
-   `AetherOS->system->services->aether-runtime.service` --- start and
    supervise the model runtime independently of core boot.
-   `AetherOS->system->services->aether-broker.service` --- provide the
    validated capability gateway.
-   `AetherOS->system->services->aether-agent.service` --- run Miso as
    an unprivileged user-space agent.
-   `AetherOS->system->services->aether-intentfs.service` --- track
    supported file events and maintain the semantic index.
-   `AetherOS->system->services->aether-ledger.service` --- persist
    privacy-aware action records.
-   `AetherOS->system->services->aether-workspace.service` --- persist
    and restore user-approved Living Workspaces.
-   `AetherOS->system->services->aether-notification.service` ---
    deliver real system and application notifications.
-   `AetherOS->system->services->aether-update-check.service` --- check
    configured signed update metadata under the user's update policy.
-   `AetherOS->system->services->aether-health.service` --- publish
    actual service and resource health.
-   `AetherOS->system->services->aether-backup.service` --- execute
    configured backups and report verified state.
-   `AetherOS->system->services->aether-recovery.service` --- coordinate
    installed recovery capabilities.
-   `AetherOS->system->logging->redaction-rules.yaml` --- redact
    credentials and sensitive values from logs and exported diagnostics.
-   `AetherOS->system->health->failure-recovery-map.yaml` --- map
    service failures to actual recovery actions and user-visible
    explanations.

Use a maintained init/service manager and real Linux service facilities.
Service definitions must specify service identity, permissions,
dependencies, resource limits, restart behavior, shutdown behavior,
logging and sandboxing. Do not invent a custom init system merely to
appear novel.

## 4.5 Core hardware, storage, accounts and networking services

-   `AetherOS->services->hardware->hardware-probe->main.*` --- expose a
    stable hardware profile assembled from real system interfaces.
-   `AetherOS->services->hardware->hardware-probe->cpu_probe.*` ---
    collect CPU model, core topology and supported instruction sets.
-   `AetherOS->services->hardware->hardware-probe->memory_probe.*` ---
    collect installed RAM, available headroom, memory pressure and
    swap/zram state.
-   `AetherOS->services->hardware->hardware-probe->accelerator_probe.*`
    --- discover supported GPU/NPU devices and available drivers without
    assuming an accelerator exists.
-   `AetherOS->services->hardware->hardware-probe->storage_probe.*` ---
    collect disk capacity, free space, filesystem and supported health
    information.
-   `AetherOS->services->hardware->hardware-probe->network_probe.*` ---
    report actual interfaces and link state.
-   `AetherOS->services->hardware->hardware-probe->thermal_probe.*` ---
    expose temperature and thermal state only where supported.
-   `AetherOS->services->hardware->hardware-probe->hardware_profile.schema.json`
    --- define a versioned schema for detected hardware facts and
    unknown values.
-   `AetherOS->services->hardware->power-manager->power_manager.*` ---
    implement power profiles, suspend/resume and battery-aware policy.
-   `AetherOS->services->account->account-service->user_create.*` ---
    create users using the system account mechanisms and safe defaults.
-   `AetherOS->services->account->account-service->group_policy.*` ---
    manage supported group membership and permissions.
-   `AetherOS->services->account->authentication->auth_provider.*` ---
    integrate the selected authentication stack.
-   `AetherOS->services->account->session->session_manager.*` ---
    create, lock, restore and close real user sessions.
-   `AetherOS->services->storage->mount-manager->mount_service.*` ---
    mount supported filesystems under the actual user's permission
    policy.
-   `AetherOS->services->storage->mount-manager->safe_eject.*` ---
    safely unmount removable media and report busy devices accurately.
-   `AetherOS->services->storage->trash->trash_service.*` --- move
    deletable user files to a recoverable trash location.
-   `AetherOS->services->storage->trash->restore_service.*` --- restore
    trashed files without overwriting conflicting files silently.
-   `AetherOS->services->networking->network-service->network_service.*`
    --- integrate Wi-Fi, Ethernet, DNS and connection state with the
    selected network manager.
-   `AetherOS->services->networking->firewall->firewall_policy.*` ---
    manage firewall policy through supported system tooling and
    privileged authorization.
-   `AetherOS->services->networking->network-consent->per_capability_network_policy.*`
    --- control whether a capability can send data over the network.
-   `AetherOS->services->audio->audio-service->audio_service.*` ---
    integrate the chosen audio server, device selection, volume and
    per-app streams.
-   `AetherOS->services->audio->audio-service->microphone_permission.*`
    --- enforce microphone permission and expose a visible capture
    state.
-   `AetherOS->services->time->clock-service->timezone_service.*` ---
    manage time zone and locale-aware date/time display.
-   `AetherOS->services->time->scheduler->reminder_service.*` ---
    persist reminders with explicit user intent and visible scheduling.
-   `AetherOS->services->notifications->notification_service.*` ---
    publish actionable notifications from actual service events.
-   `AetherOS->services->clipboard->sensitive_content_filter.*` ---
    avoid retaining sensitive clipboard content against policy.
-   `AetherOS->services->printing->print_service.*` --- connect to a
    supported printing system and expose actual queue state.
-   `AetherOS->services->logging->diagnostic_bundle.*` --- collect an
    explicitly approved, redacted diagnostic bundle.
-   `AetherOS->services->backup->backup_service.*` --- create real
    backups, verify manifests and report restore capability.

## 4.6 IPC and shared libraries

-   `AetherOS->libraries->libaether-core->include->aether_core->result.h`
    --- define typed success/failure results used consistently across
    services.
-   `AetherOS->libraries->libaether-core->include->aether_core->cancellation.h`
    --- define cancellation and timeout propagation.
-   `AetherOS->libraries->libaether-core->include->aether_core->resource_limits.h`
    --- define shared resource-budget structures.
-   `AetherOS->libraries->libaether-ipc->include->aether_ipc->client.h`
    --- implement authenticated local IPC clients.
-   `AetherOS->libraries->libaether-ipc->include->aether_ipc->server.h`
    --- implement local IPC service endpoints with access control.
-   `AetherOS->libraries->libaether-ipc->include->aether_ipc->schema_validation.h`
    --- validate request and response schemas before use.
-   `AetherOS->libraries->libaether-config->src->config_store.*` ---
    read and write versioned configuration safely.
-   `AetherOS->libraries->libaether-config->src->config_migration.*` ---
    migrate older configuration without losing user settings.
-   `AetherOS->libraries->libaether-files->src->file_identity.*` ---
    create stable file identity and detect rename/move changes.
-   `AetherOS->libraries->libaether-files->src->permission_check.*` ---
    query actual filesystem permissions before file actions.
-   `AetherOS->libraries->libaether-ui->src->keyboard_navigation.*` ---
    provide consistent keyboard navigation support.
-   `AetherOS->libraries->libaether-ui->src->reduced_motion.*` --- honor
    reduced-motion preferences in native UI components.
-   `AetherOS->protocols->dbus->org.aether.Runtime.xml` --- define the
    versioned Runtime IPC interface.
-   `AetherOS->protocols->dbus->org.aether.IntentFS.xml` --- define
    semantic indexing and search methods.
-   `AetherOS->protocols->dbus->org.aether.CapabilityBroker.xml` ---
    define validated capability requests and results.
-   `AetherOS->protocols->dbus->org.aether.ActionLedger.xml` --- define
    action history and retention methods.
-   `AetherOS->protocols->dbus->org.aether.Workspaces.xml` --- define
    workspace save, preview and restore operations.
-   `AetherOS->protocols->dbus->org.aether.Settings.xml` --- define
    typed settings operations.
-   `AetherOS->protocols->schemas->capability-request.schema.json` ---
    define capability request inputs and identity context.
-   `AetherOS->protocols->schemas->capability-result.schema.json` ---
    define truthful results, errors and recovery metadata.
-   `AetherOS->protocols->schemas->action-plan.schema.json` --- define
    structured action plans and risk annotations.
-   `AetherOS->protocols->schemas->action-ledger-entry.schema.json` ---
    define audit event fields and redaction rules.
-   `AetherOS->protocols->schemas->hardware-profile.schema.json` ---
    define hardware facts consumed by Runtime.
-   `AetherOS->protocols->schemas->inference-request.schema.json` ---
    define bounded inference requests, task class and cancellation.
-   `AetherOS->protocols->schemas->inference-response.schema.json` ---
    define streamed/final inference output and errors.
-   `AetherOS->protocols->schemas->intentfs-record.schema.json` ---
    define file metadata, index status and the three concepts.
-   `AetherOS->protocols->schemas->workspace.schema.json` --- define
    portable, versioned workspace state.

## 4.7 Native desktop shell and visual fidelity

-   `AetherOS->desktop->shell->app_main.*` --- start the actual native
    desktop process and initialize required components.
-   `AetherOS->desktop->shell->shell_controller.*` --- coordinate shell
    state and connect controls to live services.
-   `AetherOS->desktop->shell->shell_startup.*` --- restore
    user-approved shell settings and launch the session safely.
-   `AetherOS->desktop->compositor->wayland_session.*` --- start and
    integrate the supported native Wayland session.
-   `AetherOS->desktop->compositor->display_manager.*` --- manage
    displays, scaling, resolution and supported multi-monitor layouts.
-   `AetherOS->desktop->window-manager->window_manager.*` --- track real
    application windows, focus, z-order and lifecycle.
-   `AetherOS->desktop->window-manager->move_resize.*` --- implement
    native window movement and resizing.
-   `AetherOS->desktop->window-manager->virtual_desktops.*` ---
    implement virtual desktop state and switching.
-   `AetherOS->desktop->panels->top_bar->top_bar.*` --- render live
    status, time and system indicators.
-   `AetherOS->desktop->panels->taskbar->taskbar.*` --- launch
    applications and show real running/active window state.
-   `AetherOS->desktop->panels->notification_center->notification_center.*`
    --- show actual system/application notifications.
-   `AetherOS->desktop->panels->activity_panel->activity_panel.*` ---
    display real recent system and agent events.
-   `AetherOS->desktop->panels->focus_chip->focus_chip.*` --- show the
    real focus session state and controls.
-   `AetherOS->desktop->launcher->app_launcher.*` --- enumerate
    installed applications from real desktop entries.
-   `AetherOS->desktop->launcher->command_search.*` --- search
    applications and supported system actions without executing
    arbitrary model output.
-   `AetherOS->desktop->windows->window_frame.*` --- draw native window
    chrome consistent with the supplied reference.
-   `AetherOS->desktop->windows->window_controls.*` --- implement actual
    close, minimize and maximize operations.
-   `AetherOS->desktop->theme->palette.yaml` --- define the approved
    Aether color palette.
-   `AetherOS->desktop->theme->typography.yaml` --- define type styles
    and scaling rules.
-   `AetherOS->desktop->theme->motion.yaml` --- define animation timing
    and reduced-motion behavior.
-   `AetherOS->desktop->miso-view->miso_companion_view.*` --- render the
    cat companion in the native desktop and connect its states to real
    agent activity.
-   `AetherOS->desktop->miso-view->miso_speech_bubble.*` --- show actual
    agent messages, status and errors.
-   `AetherOS->desktop->focus-mode->focus_controller.*` --- start,
    pause, resume and end a real focus session.
-   `AetherOS->desktop->dialogs->permission_dialog.*` --- show the exact
    capability, resource and permission being requested.
-   `AetherOS->desktop->dialogs->destructive_action_dialog.*` ---
    require explicit confirmation for destructive operations.
-   `AetherOS->desktop->notifications->toast_manager.*` --- show real,
    dismissible transient notifications.
-   `AetherOS->desktop->accessibility->accessible_tree.*` --- expose
    native semantic roles and accessible names.
-   `AetherOS->desktop->accessibility->screen_reader_bridge.*` ---
    integrate with the selected accessibility stack.
-   `AetherOS->desktop->accessibility->reduced_motion.*` --- suppress or
    simplify animations when requested.
-   `AetherOS->desktop->assets->miso->miso.svg` --- provide the approved
    cat artwork in the native shell.
-   `AetherOS->desktop->assets->miso->miso-walk.svg` --- provide the
    walk state artwork/animation if the reference includes it.
-   `AetherOS->desktop->assets->miso->miso-run.svg` --- provide the run
    state artwork/animation if the reference includes it.
-   `AetherOS->desktop->assets->miso->miso-jump.svg` --- provide the
    jump state artwork/animation if the reference includes it.

Reproduce the supplied design's warm background, translucent top bar,
brand mark, desktop icons, window chrome, taskbar, Miso
idle/walk/run/jump/sleep/focus/search/carry states, speech bubble,
assistant panel, activity panel, focus chip, toasts, settings
persistence, keyboard behavior and reduced-motion support. Preserve the
supplied SVG artwork where permitted. Do not ship the HTML reference as
the shell. Window movement, focus, resizing, display layout and app
lifecycle must be controlled by native desktop APIs, not browser-style
absolute positioning.

## 4.8 Native applications

-   `AetherOS->applications->app-framework->application_context.*` ---
    expose app identity, settings, IPC and lifecycle services to
    built-in applications.
-   `AetherOS->applications->files->main.*` --- launch the native file
    manager.
-   `AetherOS->applications->files->file_list_model.*` --- list real
    directory contents with correct permissions and errors.
-   `AetherOS->applications->files->file_operations.*` --- implement
    real copy, move, rename, trash, restore and safe conflict handling.
-   `AetherOS->applications->files->file_metadata_view.*` --- display
    real file metadata and permission information.
-   `AetherOS->applications->files->intentfs_search_panel.*` --- search
    IntentFS and display matching reasons/concepts.
-   `AetherOS->applications->files->concept_chips.*` --- display exactly
    the three validated concepts when available and the truthful index
    state otherwise.
-   `AetherOS->applications->writer->document_model.*` --- represent
    actual editable document content.
-   `AetherOS->applications->writer->document_storage.*` --- open and
    save real documents using supported formats.
-   `AetherOS->applications->writer->autosave.*` --- persist recoverable
    drafts and report unsaved changes accurately.
-   `AetherOS->applications->writer->recovery_drafts.*` --- restore
    drafts after interruption without overwriting user files silently.
-   `AetherOS->applications->terminal->pty_session.*` --- create a real
    pseudo-terminal session.
-   `AetherOS->applications->terminal->shell_process.*` --- launch the
    configured user shell with correct working directory and process
    lifecycle.
-   `AetherOS->applications->terminal->copy_paste.*` --- implement
    native terminal selection and clipboard integration.
-   `AetherOS->applications->code->editor_buffer.*` --- provide real
    file-backed editing with save and dirty-state behavior.
-   `AetherOS->applications->code->project_folder.*` --- open a
    user-selected project directory without inventing files.
-   `AetherOS->applications->code->local_code_assist.*` --- request
    optional assistance through Aether Runtime under local privacy
    policy.
-   `AetherOS->applications->gallery->image_browser.*` --- list and
    display real supported image files.
-   `AetherOS->applications->calculator->expression_parser.*` --- parse
    and evaluate supported expressions safely.
-   `AetherOS->applications->clock->timezone_view.*` --- show actual
    time and time-zone information.
-   `AetherOS->applications->focus->focus_session.*` --- persist focus
    sessions and connect them to desktop focus mode.
-   `AetherOS->applications->system-monitor->process_table.*` ---
    display real process data from supported system interfaces.
-   `AetherOS->applications->system-monitor->cpu_graph.*` --- graph real
    CPU readings.
-   `AetherOS->applications->system-monitor->memory_graph.*` --- graph
    real memory and pressure readings.
-   `AetherOS->applications->system-monitor->service_status_view.*` ---
    display actual service state and error details.
-   `AetherOS->applications->settings->network_page.*` --- read and
    change supported network settings through the network manager.
-   `AetherOS->applications->settings->privacy_page.*` --- manage real
    privacy controls and data retention.
-   `AetherOS->applications->settings->permissions_page.*` --- show and
    modify authorized application/capability permissions.
-   `AetherOS->applications->settings->ai_runtime_page.*` --- display
    Runtime status, hardware profile, installed models and actual
    resource usage.
-   `AetherOS->applications->settings->intentfs_page.*` --- manage
    indexing scope, exclusions, pause/resume and reindex actions.
-   `AetherOS->applications->settings->updates_page.*` --- show actual
    update metadata, release notes and transaction state.
-   `AetherOS->applications->software-center->repository_browser.*` ---
    browse configured trusted repositories.
-   `AetherOS->applications->software-center->signature_status.*` ---
    show verified signature/integrity state from the package system.
-   `AetherOS->applications->software-center->install_transaction.*` ---
    preview and execute real package installation with required
    authorization.
-   `AetherOS->applications->screenshot->screenshot_service.*` ---
    capture a selected display/window/region using native APIs.
-   `AetherOS->applications->archive-manager->archive_extract.*` ---
    safely extract supported archive formats with path traversal
    protections.
-   `AetherOS->applications->backup-center->restore_wizard.*` ---
    preview and perform a real restore operation.
-   `AetherOS->applications->recovery-center->recovery_dashboard.*` ---
    show real recovery, rollback, model repair and index-rebuild
    options.
-   `AetherOS->applications->mines->game_logic.*` --- implement the
    actual standalone game logic rather than a static game mock-up.

Each built-in application must have a desktop entry, icon, localization
domain, accessible controls, real persistence where relevant, clear
error states, package metadata and appropriate IPC/service integration.
A menu item must not be displayed as installed unless the corresponding
application package exists.

## 4.9 Aether Runtime and first-boot model setup

-   `AetherOS->ai->runtime->daemon->main.*` --- launch the independent
    Runtime daemon.
-   `AetherOS->ai->runtime->daemon->runtime_service.*` --- own model
    lifecycle, inference routing, status and API operations.
-   `AetherOS->ai->runtime->api->inference_api.*` --- expose versioned
    local inference requests with bounded input, output, timeout and
    cancellation.
-   `AetherOS->ai->runtime->api->response_stream.*` --- stream inference
    output without blocking the desktop.
-   `AetherOS->ai->runtime->hardware-profile->profiler.*` --- collect
    hardware measurements through actual system interfaces.
-   `AetherOS->ai->runtime->hardware-profile->ram_headroom.*` ---
    estimate safe model memory budget from current availability, OS
    reserve and concurrent workload.
-   `AetherOS->ai->runtime->hardware-profile->gpu_probe.*` --- determine
    supported accelerator availability, driver and usable memory where
    exposed.
-   `AetherOS->ai->runtime->hardware-profile->storage_budget.*` ---
    verify download and installation space before any large download.
-   `AetherOS->ai->runtime->recommendation->recommendation_engine.*` ---
    rank compatible models for the selected task and machine.
-   `AetherOS->ai->runtime->recommendation->memory_estimator.*` ---
    estimate model weights, runtime overhead, context/KV cache and
    concurrent memory use.
-   `AetherOS->ai->runtime->recommendation->latency_estimator.*` ---
    provide a grounded performance estimate with uncertainty, not a
    guaranteed speed.
-   `AetherOS->ai->runtime->recommendation->compatibility_filter.*` ---
    reject models incompatible with hardware, format, backend, license
    or available disk space.
-   `AetherOS->ai->runtime->model-catalog->catalog_loader.*` --- load a
    versioned model catalog from approved sources.
-   `AetherOS->ai->runtime->model-catalog->catalog_signature.*` ---
    verify catalog authenticity before trusting entries.
-   `AetherOS->ai->runtime->model-catalog->model_profile.schema.json`
    --- describe model format, size, license, hardware needs, supported
    tasks, hashes and source.
-   `AetherOS->ai->runtime->model-manager->model_registry.*` --- track
    installed models and their verified state.
-   `AetherOS->ai->runtime->model-manager->model_install.*` --- install
    model artifacts transactionally into the configured model store.
-   `AetherOS->ai->runtime->model-manager->model_remove.*` --- remove a
    selected model safely and report reclaimed storage.
-   `AetherOS->ai->runtime->download->download_manager.*` --- perform
    resumable, cancellable downloads from approved sources.
-   `AetherOS->ai->runtime->download->disk_space_guard.*` --- stop a
    download/install before exhausting the filesystem.
-   `AetherOS->ai->runtime->download->manifest_verifier.*` --- verify
    artifact metadata and expected file list.
-   `AetherOS->ai->runtime->download->digest_verifier.*` --- verify
    downloaded artifact digests against trusted metadata.
-   `AetherOS->ai->runtime->download->license_acceptance.*` --- record
    any required license acceptance before download/use.
-   `AetherOS->ai->runtime->backend->backend_interface.*` --- define a
    stable backend contract independent of one inference engine.
-   `AetherOS->ai->runtime->backend->backend_registry.*` --- discover
    supported, installed backends and their capabilities.
-   `AetherOS->ai->runtime->backend->llama_cpp_adapter.*` --- adapt the
    selected compatible native inference backend when included and
    licensed.
-   `AetherOS->ai->runtime->inference->inference_scheduler.*` ---
    schedule interactive and background requests with priority and
    fairness.
-   `AetherOS->ai->runtime->inference->context_manager.*` --- bound
    context size and prevent unsafe memory overcommit.
-   `AetherOS->ai->runtime->inference->kv_cache_budget.*` --- enforce
    memory budget for inference cache.
-   `AetherOS->ai->runtime->queues->backpressure.*` --- slow or reject
    background work under pressure rather than destabilize the OS.
-   `AetherOS->ai->runtime->resource-governor->memory_pressure_handler.*`
    --- reduce context, pause indexing or unload models before critical
    pressure.
-   `AetherOS->ai->runtime->resource-governor->unload_idle_model.*` ---
    release model memory according to configured idle policy.
-   `AetherOS->ai->runtime->resource-governor->battery_policy.*` ---
    adapt background inference to power preferences.
-   `AetherOS->ai->runtime->resource-governor->thermal_policy.*` ---
    throttle or pause inference when supported thermal signals require
    it.
-   `AetherOS->ai->runtime->validation->model_integrity.*` --- verify
    installed model files before loading.
-   `AetherOS->ai->runtime->validation->inference_smoke_check.*` --- run
    a bounded, harmless inference to verify that the selected model
    actually works.
-   `AetherOS->ai->runtime->privacy->local_endpoint_policy.*` ---
    restrict inference endpoints to local access unless a separately
    authorized remote feature is enabled.
-   `AetherOS->ai->runtime->privacy->prompt_log_policy.*` --- avoid
    retaining prompts or outputs beyond the configured policy.
-   `AetherOS->ai->firstboot->firstboot_controller.*` --- coordinate
    first-run setup and persist resumable progress.
-   `AetherOS->ai->firstboot->hardware_summary.*` --- show detected
    hardware facts and unknown/unsupported fields honestly.
-   `AetherOS->ai->firstboot->model_recommendation_page.*` --- explain
    recommended model choices, limitations, storage and license details.
-   `AetherOS->ai->firstboot->model_download_page.*` --- allow explicit
    consent, progress, cancel and retry for model download.
-   `AetherOS->ai->firstboot->model_validation_page.*` --- report
    integrity, backend setup and actual inference verification.
-   `AetherOS->ai->firstboot->no_model_mode.*` --- finish setup and
    preserve a fully usable OS when the user skips model installation.
-   `AetherOS->ai->catalog->catalog.schema.json` --- validate model
    catalog records.
-   `AetherOS->ai->policies->model-license-policy.yaml` --- enforce
    source and license requirements.
-   `AetherOS->ai->policies->download-consent-policy.yaml` --- define
    required user approval and cancellation behavior.
-   `AetherOS->ai->policies->resource-budget-policy.yaml` --- set safe
    system resource reserves and background-work limits.
-   `AetherOS->ai->policies->no-network-default.yaml` --- prevent silent
    remote inference or private-data upload by default.

Runtime must not depend on Ollama as a required product component. It
may use a documented pluggable backend internally. Do not label an
arbitrary model "best" without checking the model's actual format,
license, context, task suitability, system headroom, backend
compatibility and disk needs. If no compatible model is available,
explain why and allow setup to finish.

## 4.10 IntentFS semantic file service

-   `AetherOS->intentfs->daemon->main.*` --- start the IntentFS service
    independently of the file manager.
-   `AetherOS->intentfs->watcher->filesystem_watcher.*` --- watch
    configured user paths for create/change/delete/move events using
    supported filesystem notifications.
-   `AetherOS->intentfs->watcher->rename_move_tracker.*` --- preserve
    stable identity when a file is renamed or moved where the underlying
    identity permits.
-   `AetherOS->intentfs->watcher->missed_event_reconciler.*` ---
    reconcile index state after missed events, restart or
    removable-drive changes.
-   `AetherOS->intentfs->pipeline->job_scheduler.*` --- schedule
    indexing jobs with priorities, cancellation and bounded concurrency.
-   `AetherOS->intentfs->pipeline->low_resource_pause.*` --- pause or
    throttle background indexing under memory, battery or thermal
    pressure.
-   `AetherOS->intentfs->extraction->extractor_interface.*` --- define a
    safe interface for supported file extractors.
-   `AetherOS->intentfs->extraction->plain_text_extractor.*` --- extract
    bounded text from supported plain-text files.
-   `AetherOS->intentfs->extraction->markdown_extractor.*` --- extract
    Markdown content while preserving useful headings and text.
-   `AetherOS->intentfs->extraction->pdf_text_extractor.*` --- extract
    text from supported PDF files with size and parser limits.
-   `AetherOS->intentfs->extraction->office_document_extractor.*` ---
    extract text and metadata from explicitly supported office formats.
-   `AetherOS->intentfs->extraction->source_code_extractor.*` ---
    extract source text and language metadata from supported code files.
-   `AetherOS->intentfs->extraction->mime_detection.*` --- identify file
    types using content and system MIME facilities rather than filename
    alone.
-   `AetherOS->intentfs->extraction->file_size_limits.*` --- bound
    parser resource use and mark unsupported/oversized files clearly.
-   `AetherOS->intentfs->concepts->concept_prompt.*` --- create a
    constrained prompt using only the file's permitted extracted
    content.
-   `AetherOS->intentfs->concepts->concept_generator.*` --- request
    local-model generation of file concepts through Runtime.
-   `AetherOS->intentfs->concepts->concept_normalizer.*` --- normalize
    case, whitespace and equivalent formatting.
-   `AetherOS->intentfs->concepts->concept_validator.*` --- reject
    empty, duplicate, generic or malformed concepts according to the
    defined policy.
-   `AetherOS->intentfs->concepts->uniqueness_validator.*` --- ensure
    all three concepts are distinct.
-   `AetherOS->intentfs->concepts->exactly_three_enforcer.*` --- persist
    exactly three validated concepts for each successfully indexed
    supported file.
-   `AetherOS->intentfs->concepts->bounded_retry.*` --- retry invalid
    model output a bounded number of times, then record pending/failed
    state rather than invent concepts.
-   `AetherOS->intentfs->index->metadata_store.*` --- persist stable
    file ID, path, type, timestamps, fingerprint, permissions,
    extraction status and concepts.
-   `AetherOS->intentfs->index->schema.sql` --- define the actual
    metadata database schema and constraints.
-   `AetherOS->intentfs->index->stable_file_id.*` --- maintain stable
    identity where supported and handle identity changes explicitly.
-   `AetherOS->intentfs->index->content_fingerprint.*` --- detect
    changed content without rewriting the original file.
-   `AetherOS->intentfs->index->index_transaction.*` --- atomically
    update a record so partial concepts are not exposed as a successful
    record.
-   `AetherOS->intentfs->index->tombstone_policy.*` --- remove stale
    index records when files disappear while respecting retention rules.
-   `AetherOS->intentfs->index->rebuild_index.*` --- rebuild the
    semantic index without changing original files.
-   `AetherOS->intentfs->search->search_service.*` --- expose local
    search through a versioned API.
-   `AetherOS->intentfs->search->filename_search.*` --- provide fast
    exact and partial filename matching independent of model
    availability.
-   `AetherOS->intentfs->search->concept_search.*` --- match queries
    against validated concepts.
-   `AetherOS->intentfs->search->extracted_text_search.*` --- search
    extracted text only for supported and permitted files.
-   `AetherOS->intentfs->search->ranking.*` --- rank by grounded
    filename/path/concept/content signals and clearly expose match
    reasons.
-   `AetherOS->intentfs->privacy->folder_exclusions.*` --- enforce
    excluded paths and user-defined indexing exclusions.
-   `AetherOS->intentfs->privacy->per_user_scope.*` --- prevent
    cross-user content leakage.
-   `AetherOS->intentfs->privacy->removable_drive_policy.*` --- follow
    consent and policy for removable storage.
-   `AetherOS->intentfs->privacy->index_delete_only.*` --- clear index
    metadata without deleting source files.
-   `AetherOS->intentfs->ui->index_status.*` --- display current
    indexing progress and pending/failed state from the service.
-   `AetherOS->intentfs->ui->indexing_error_view.*` --- explain actual
    extraction, model or permission failures.
-   `AetherOS->intentfs->ui->exclusion_manager.*` --- manage excluded
    paths through the real policy service.

The three concepts must be generated from the file's permitted content
by the local model. Do not hard-code concepts or use a fixed list of
keywords as if they were model predictions. A supported file may be
pending, excluded or failed; only a successful indexed record may be
shown as having three concepts. Indexing must never block ordinary file
access, modify file bytes, cross user permissions, or treat document
contents as trusted agent instructions.

## 4.11 Miso, CapabilityOS, broker, policy and Action Ledger

-   `AetherOS->miso->agent->agent_service.*` --- run the Miso agent as
    an unprivileged service.
-   `AetherOS->miso->agent->context_builder.*` --- gather only relevant,
    permitted conversation and system context.
-   `AetherOS->miso->agent->intent_classifier.*` --- classify the user's
    request and identify missing information.
-   `AetherOS->miso->agent->task_planner.*` --- create a structured plan
    with expected effects and risk.
-   `AetherOS->miso->agent->plan_decomposer.*` --- break complex
    requests into bounded, inspectable capability calls.
-   `AetherOS->miso->agent->capability_selector.*` --- select only
    registered capabilities whose schemas and permissions match the
    task.
-   `AetherOS->miso->agent->execution_orchestrator.*` --- execute
    approved steps, track results and stop on failure.
-   `AetherOS->miso->agent->result_verifier.*` --- compare the reported
    result with actual service state before claiming success.
-   `AetherOS->miso->agent->task_cancellation.*` --- propagate
    stop/cancel and enforce timeouts and task budgets.
-   `AetherOS->miso->capability-os->registry->capability_registry.*` ---
    register supported capabilities and their versions, input schemas,
    permission needs and side effects.
-   `AetherOS->miso->capability-os->registry->capability.schema.json`
    --- define the complete capability contract.
-   `AetherOS->miso->capability-os->schemas->files.capabilities.json`
    --- define typed file
    search/open/copy/move/rename/trash/restore/index actions.
-   `AetherOS->miso->capability-os->schemas->writer.capabilities.json`
    --- define document create/open/save operations.
-   `AetherOS->miso->capability-os->schemas->system-status.capabilities.json`
    --- define read-only system status and diagnostic capabilities.
-   `AetherOS->miso->capability-os->schemas->model.capabilities.json`
    --- define model listing, recommendation and download lifecycle
    capabilities.
-   `AetherOS->miso->capability-os->schemas->workspace.capabilities.json`
    --- define save, preview and restore operations for Living
    Workspaces.
-   `AetherOS->miso->broker->broker_service.*` --- authenticate
    capability callers and enforce validation, permissions, risk, limits
    and confirmation.
-   `AetherOS->miso->broker->request_authentication.*` --- establish the
    caller identity and session context.
-   `AetherOS->miso->broker->schema_validation.*` --- reject malformed
    or unknown request fields.
-   `AetherOS->miso->broker->identity_check.*` --- verify the caller and
    target user/session.
-   `AetherOS->miso->broker->permission_check.*` --- check current
    permissions against the actual target resources.
-   `AetherOS->miso->broker->risk_classifier.*` --- categorize
    read-only, reversible, externally visible and destructive actions.
-   `AetherOS->miso->broker->confirmation_policy.*` --- require explicit
    confirmation for consequential actions.
-   `AetherOS->miso->broker->rate_limiter.*` --- bound action frequency
    and prevent loops.
-   `AetherOS->miso->broker->idempotency_store.*` --- prevent duplicate
    execution on retry where the operation supports idempotency.
-   `AetherOS->miso->broker->execution_dispatcher.*` --- dispatch only
    registered capability implementations.
-   `AetherOS->miso->broker->timeout_and_cancellation.*` --- enforce
    deadlines and cancellation.
-   `AetherOS->miso->broker->result_verification.*` --- obtain actual
    operation outcome from the owning service.
-   `AetherOS->miso->broker->rollback_dispatcher.*` --- invoke a
    documented undo/compensation path where feasible.
-   `AetherOS->miso->policy-engine->default-policy.yaml` --- define safe
    default permissions.
-   `AetherOS->miso->policy-engine->read-only-policy.yaml` --- define
    non-mutating actions and their limits.
-   `AetherOS->miso->policy-engine->reversible-action-policy.yaml` ---
    define permitted reversible actions and required preview.
-   `AetherOS->miso->policy-engine->write-action-policy.yaml` --- define
    write operations and authorization.
-   `AetherOS->miso->policy-engine->destructive-action-policy.yaml` ---
    define destructive actions, confirmation and recovery requirements.
-   `AetherOS->miso->capabilities->files->search_files.*` --- search
    actual files through IntentFS and permitted filesystem APIs.
-   `AetherOS->miso->capabilities->files->copy_file.*` --- copy a real
    file after path and permission validation.
-   `AetherOS->miso->capabilities->files->move_file.*` --- move a real
    file with conflict handling and a truthful result.
-   `AetherOS->miso->capabilities->files->move_to_trash.*` --- use
    recoverable trash for user-file deletion where possible.
-   `AetherOS->miso->capabilities->apps->open_app.*` --- launch an
    installed app using the native app registry.
-   `AetherOS->miso->capabilities->system->get_cpu_memory_status.*` ---
    return actual system metrics from supported interfaces.
-   `AetherOS->miso->capabilities->models->recommend_model.*` --- return
    the Runtime's current compatibility-ranked recommendations.
-   `AetherOS->miso->ledger->ledger_service.*` --- persist and retrieve
    user-visible action history.
-   `AetherOS->miso->ledger->append_record.*` --- append a structured
    action record after recording the relevant permission and execution
    state.
-   `AetherOS->miso->ledger->query_history.*` --- query history by date,
    capability, status and target.
-   `AetherOS->miso->ledger->redact_secrets.*` --- redact credentials
    and sensitive values before persistence.
-   `AetherOS->miso->ledger->retention_policy.*` --- apply visible
    retention and deletion policy without allowing the agent to erase
    protected history.
-   `AetherOS->miso->ledger->schema.sql` --- define persistent action
    history with schema migration support.
-   `AetherOS->miso->workspaces->workspace_service.*` --- save and
    restore project-aware workspace state.
-   `AetherOS->miso->workspaces->layout_capture.*` --- capture supported
    window/layout state without recording unrelated private data.
-   `AetherOS->miso->workspaces->restore_preview.*` --- show proposed
    apps, files and layout changes before restoration.
-   `AetherOS->miso->workspaces->restore_executor.*` --- restore only
    user-approved workspace state; never auto-run terminal commands.
-   `AetherOS->miso->safety->untrusted_content_boundary.*` --- keep
    retrieved files, webpages, filenames and terminal output from
    altering policy.
-   `AetherOS->miso->safety->no_shell_interpolation.*` --- prevent model
    output from being concatenated into shell commands.
-   `AetherOS->miso->safety->bounded_loop_guard.*` --- stop repeated or
    unbounded agent execution.
-   `AetherOS->miso->ui->assistant_panel.*` --- display real
    runtime/agent status, conversation, errors and cancellation.
-   `AetherOS->miso->ui->plan_preview.*` --- show proposed operations
    and target resources before consequential execution.
-   `AetherOS->miso->ui->capability_confirmation.*` --- collect explicit
    approval when required by policy.
-   `AetherOS->miso->ui->action_progress.*` --- display real step state
    and allow cancellation.
-   `AetherOS->miso->ui->action_history_view.*` --- display ledger
    entries and available recovery actions.
-   `AetherOS->miso->ui->undo_action_view.*` --- offer only a real
    supported undo/compensation operation.

The model must return structured capability requests, never privileged
shell commands. Every request must be validated against schemas, user
identity, current filesystem permissions, policy, rate limits and risk.
The interface must distinguish requested, authorized, running,
completed, failed, cancelled and partially completed states. Never claim
success without a verified result. Show the target and effect before
consequential operations, and record the decision and outcome.

## 4.12 Security, privacy and system trust

-   `AetherOS->security->identity->service-users.yaml` --- define
    separate least-privilege identities for services.
-   `AetherOS->security->authorization->capability-permissions.yaml` ---
    map capabilities to permission requirements and resource scopes.
-   `AetherOS->security->sandbox->agent-sandbox.conf` --- run agent
    planning under the selected OS sandbox controls.
-   `AetherOS->security->sandbox->runtime-sandbox.conf` --- constrain
    model execution and Runtime service access.
-   `AetherOS->security->sandbox->indexer-sandbox.conf` --- constrain
    parsers and indexing workers.
-   `AetherOS->security->hardening->kernel-hardening.yaml` --- document
    enabled kernel hardening and tradeoffs.
-   `AetherOS->security->hardening->service-hardening.yaml` --- set
    service sandboxing, restricted paths and resource limits.
-   `AetherOS->security->hardening->filesystem-permissions.yaml` ---
    define owner/group/mode policy for system files.
-   `AetherOS->security->cryptography->artifact-verification.*` ---
    verify package, catalog and release artifacts against trusted
    metadata.
-   `AetherOS->security->secrets->secret-store-interface.*` --- use an
    appropriate OS secret store rather than plaintext config files.
-   `AetherOS->security->secrets->secret-redaction.*` --- redact secrets
    in logs, prompts and diagnostic exports.
-   `AetherOS->security->privacy->local-first-defaults.yaml` --- keep
    inference and indexed content local by default.
-   `AetherOS->security->privacy->telemetry-policy.yaml` --- define
    transparent telemetry behavior and default opt-out/consent rules.
-   `AetherOS->security->privacy->model-download-consent.yaml` ---
    require explicit consent for model downloads.
-   `AetherOS->security->privacy->microphone-consent.yaml` --- require
    explicit voice-input permission and visible microphone state.
-   `AetherOS->security->privacy->data-retention.yaml` --- define
    retention periods and deletion/export behavior.
-   `AetherOS->security->audit->audit-policy.yaml` --- define events
    that must be recorded and protected.
-   `AetherOS->security->threat-model->trust-boundaries.md` --- identify
    trusted and untrusted processes/data.
-   `AetherOS->security->threat-model->prompt-injection.md` --- specify
    defenses for malicious instructions in files and retrieved content.
-   `AetherOS->security->threat-model->malicious-model-artifacts.md` ---
    define safe model-source, integrity and loading policy.

No model or document content may change system policy. Never store
passwords, access tokens or private keys in source, model prompts,
action history or logs. Do not silently upload file contents, prompts,
extracted text, or diagnostics. Any external transfer must identify the
destination and data category and require the authorization defined by
policy.

## 4.13 Networking, devices and firmware

-   `AetherOS->networking->connection-manager->connection_manager.*` ---
    integrate supported network interfaces and real connection state.
-   `AetherOS->networking->connection-manager->wifi_scan.*` --- scan for
    networks using the network manager and report real results.
-   `AetherOS->networking->connection-manager->wifi_connect.*` ---
    connect only after appropriate user authorization.
-   `AetherOS->networking->connection-manager->dns_configuration.*` ---
    read and configure supported DNS settings.
-   `AetherOS->networking->firewall->firewall_backend.*` --- use the
    selected supported firewall backend.
-   `AetherOS->networking->network-diagnostics->connectivity_check.*`
    --- report actual connection and DNS outcomes.
-   `AetherOS->hardware->discovery->cpu_discovery.*` --- discover CPU
    identity and features.
-   `AetherOS->hardware->discovery->pci_discovery.*` --- enumerate
    supported PCI devices.
-   `AetherOS->hardware->discovery->usb_discovery.*` --- enumerate USB
    devices and attach lifecycle events.
-   `AetherOS->hardware->discovery->display_discovery.*` --- enumerate
    actual displays and supported modes.
-   `AetherOS->hardware->discovery->audio_discovery.*` --- enumerate
    actual audio devices.
-   `AetherOS->hardware->compatibility->known-devices.yaml` --- document
    hardware with confirmed support.
-   `AetherOS->hardware->compatibility->unsupported-devices.yaml` ---
    document known limitations without implying support.
-   `AetherOS->hardware->compatibility->firmware-requirements.yaml` ---
    describe firmware requirements and distribution constraints.
-   `AetherOS->firmware->manifest.yaml` --- list firmware artifacts,
    origins, hashes and licensing status.
-   `AetherOS->third-party->source-lock.yaml` --- pin third-party
    dependencies to immutable versions.
-   `AetherOS->third-party->licenses->` --- retain required third-party
    license texts and notices.
-   `AetherOS->third-party->sbom->` --- retain generated dependency
    inventory for the release.

## 4.14 Installer, first boot and account setup

-   `AetherOS->installer->app->main.*` --- start the native installer
    application.
-   `AetherOS->installer->app->installer_controller.*` --- manage
    installation state and transitions.
-   `AetherOS->installer->screens->target_disk_screen.*` --- display
    actual disks and require the user to select the intended target.
-   `AetherOS->installer->screens->partition_plan_screen.*` --- show the
    proposed partition changes before applying them.
-   `AetherOS->installer->screens->encryption_screen.*` --- configure
    optional supported disk encryption and explain recovery-key
    handling.
-   `AetherOS->installer->screens->user_account_screen.*` --- create the
    initial user with safe authentication settings.
-   `AetherOS->installer->screens->privacy_options_screen.*` --- let the
    user configure privacy and network choices.
-   `AetherOS->installer->screens->install_summary_screen.*` --- present
    the exact target disk and planned destructive changes.
-   `AetherOS->installer->screens->install_progress_screen.*` --- report
    actual package, filesystem and bootloader installation progress.
-   `AetherOS->installer->screens->failure_recovery_screen.*` ---
    explain the real failure and offer safe recovery.
-   `AetherOS->installer->storage->disk_discovery.*` --- enumerate
    actual installable storage devices.
-   `AetherOS->installer->storage->partition_planner.*` --- generate a
    validated partition plan for the selected installation mode.
-   `AetherOS->installer->storage->filesystem_creator.*` --- create the
    selected filesystem only after explicit authorization.
-   `AetherOS->installer->storage->encryption_setup.*` --- set up the
    supported encrypted storage configuration.
-   `AetherOS->installer->storage->destructive_action_guard.*` --- block
    accidental disk erasure and verify the target immediately before
    writing.
-   `AetherOS->installer->install->package_installer.*` --- install the
    actual base and selected package set to the target root.
-   `AetherOS->installer->install->kernel_installer.*` --- install the
    correct kernel and modules.
-   `AetherOS->installer->install->initramfs_installer.*` --- generate
    an initramfs for the installed hardware/storage configuration.
-   `AetherOS->installer->install->bootloader_installer.*` --- install
    and configure the bootloader for the selected supported firmware
    path.
-   `AetherOS->installer->install->base_configurator.*` --- configure
    hostname, mounts, system services, locale and boot defaults.
-   `AetherOS->installer->install->user_creator.*` --- create the
    initial user and permissions through the system account mechanism.
-   `AetherOS->installer->install->desktop_configurator.*` --- enable
    the native desktop session and default applications.
-   `AetherOS->installer->install->install_transaction.*` --- track
    installation stages and recover from interrupted installation where
    feasible.
-   `AetherOS->system->firstboot->firstboot_wizard.*` --- configure
    language, keyboard, time zone, network and privacy after first
    login.
-   `AetherOS->system->firstboot->optional_ai_setup.*` --- offer model
    setup as optional, never a prerequisite for ordinary OS use.
-   `AetherOS->system->firstboot->model_recommendation.*` --- display
    the Runtime's actual recommendations and constraints.
-   `AetherOS->system->firstboot->completion_state.*` --- persist
    completion and resume interrupted setup safely.

The installer must identify the target disk by stable device information
and display its size and existing data risk. Destructive changes require
a separate explicit confirmation. Installation must not depend on
downloading an AI model. A failed optional model download must not roll
back a valid OS installation.

## 4.15 Recovery, backup, package manager and updates

-   `AetherOS->recovery->recovery-entry->recovery_main.*` --- start the
    independent recovery environment.
-   `AetherOS->recovery->diagnostics->inspect_boot_state.*` --- inspect
    installed boot entries and boot artifacts.
-   `AetherOS->recovery->diagnostics->inspect_service_state.*` ---
    inspect service state and logs.
-   `AetherOS->recovery->diagnostics->redacted_bundle.*` --- export only
    approved, redacted diagnostic information.
-   `AetherOS->recovery->repair->package_database_repair.*` --- repair
    package database state using the selected package manager.
-   `AetherOS->recovery->repair->bootloader_repair.*` --- restore a
    valid bootloader configuration.
-   `AetherOS->recovery->repair->initramfs_rebuild.*` --- rebuild
    initramfs from installed configuration and modules.
-   `AetherOS->recovery->repair->runtime_config_reset.*` --- repair or
    reset broken Runtime configuration without deleting user files.
-   `AetherOS->recovery->repair->model_remove_broken.*` --- remove a
    corrupt model artifact and preserve unrelated model data.
-   `AetherOS->recovery->repair->intentfs_rebuild.*` --- rebuild the
    semantic index without changing source files.
-   `AetherOS->recovery->rollback->known_good_boot_entry.*` --- preserve
    a usable boot entry for the known-good system state.
-   `AetherOS->recovery->rollback->kernel_rollback.*` --- restore a
    previously installed compatible kernel where retained.
-   `AetherOS->recovery->backup->restore_preview.*` --- show the exact
    files/configuration to be restored before writing.
-   `AetherOS->package-manager->core->package_manager.*` --- provide the
    selected package system's stable Aether-facing operations.
-   `AetherOS->package-manager->core->dependency_solver.*` --- resolve
    real dependencies and report conflicts before mutation.
-   `AetherOS->package-manager->core->transaction_engine.*` --- apply
    install/remove/upgrade operations transactionally where supported.
-   `AetherOS->package-manager->repository->metadata_verifier.*` ---
    verify signed repository metadata before trusting package listings.
-   `AetherOS->package-manager->repository->signature_verifier.*` ---
    validate package/repository signatures against configured trust.
-   `AetherOS->package-manager->policy->signature_required.yaml` ---
    require signatures for configured trusted repositories.
-   `AetherOS->updater->daemon->update_service.*` --- coordinate update
    discovery, planning, application and reporting.
-   `AetherOS->updater->verification->metadata_signature.*` --- verify
    update metadata signatures.
-   `AetherOS->updater->verification->package_digest.*` --- verify
    package digests before applying updates.
-   `AetherOS->updater->planning->update_plan.*` --- generate an update
    plan including space, compatibility and reboot requirements.
-   `AetherOS->updater->apply->staged_update.*` --- stage changes before
    activation according to the selected update strategy.
-   `AetherOS->updater->apply->post_update_health.*` --- verify the
    resulting system state and trigger rollback policy when necessary.
-   `AetherOS->updater->apply->rollback_trigger.*` --- restore the
    known-good state when the defined failure policy is met.
-   `AetherOS->updater->model-updates->model_catalog_update.*` ---
    update model metadata separately from the OS.
-   `AetherOS->updater->model-updates->model_rollback.*` --- revert a
    model update when the previous artifact is retained and valid.

Never claim a snapshot or backup exists unless it has actually been
created and verified. Keep OS, kernel, application, Runtime and model
versioning distinct. Updates must have trusted metadata, clear change
information, space checks, interruption handling and a documented
recovery path.

## 4.16 Accessibility, localization, settings and data

-   `AetherOS->accessibility->keyboard->global-shortcuts.yaml` ---
    define consistent global keyboard shortcuts.
-   `AetherOS->accessibility->screen-reader->accessible_role_map.yaml`
    --- map native controls to accessible roles and labels.
-   `AetherOS->accessibility->screen-reader->announcement_policy.yaml`
    --- announce relevant state changes without overwhelming the user.
-   `AetherOS->accessibility->visual->high-contrast-theme.yaml` ---
    provide a high-contrast theme.
-   `AetherOS->accessibility->visual->font-scaling.yaml` --- support
    readable text scaling.
-   `AetherOS->accessibility->motion->reduced-motion.yaml` --- disable
    or reduce motion when requested.
-   `AetherOS->accessibility->voice->voice-consent.yaml` --- define
    voice-input consent and indicator behavior.
-   `AetherOS->localization->locales->en->desktop.po` --- localize
    desktop UI strings.
-   `AetherOS->localization->locales->en->installer.po` --- localize
    installer strings.
-   `AetherOS->localization->locales->en->applications.po` --- localize
    built-in application strings.
-   `AetherOS->localization->locales->en->runtime.po` --- localize
    Runtime strings and model-status explanations.
-   `AetherOS->localization->locales->en->miso.po` --- localize Miso UI
    and capability confirmations.
-   `AetherOS->data->schemas->user-settings.schema.json` --- define
    versioned user settings and validation.
-   `AetherOS->data->schemas->system-settings.schema.json` --- define
    versioned system settings and validation.
-   `AetherOS->data->schemas->intentfs-record.schema.json` --- define
    persistent semantic file record fields and state.
-   `AetherOS->data->schemas->action-ledger-entry.schema.json` ---
    define action history structure and privacy fields.
-   `AetherOS->data->schemas->package-state.schema.json` --- define
    installed package state.
-   `AetherOS->data->schemas->update-state.schema.json` --- define
    update lifecycle state.
-   `AetherOS->data->migrations->README.md` --- document schema
    migration ordering, rollback limits and recovery behavior.
-   `AetherOS->assets->branding->aether-logo.svg` --- provide the
    product logo used in the native shell and installer.
-   `AetherOS->assets->desktop->palette.yaml` --- define the shared
    palette.
-   `AetherOS->assets->desktop->typography.yaml` --- define shared
    typography.
-   `AetherOS->assets->miso->` --- store approved companion artwork and
    animation states used by the native shell.

Persist system-owned mutable state in protected system data directories
and user-owned preferences/history in the user's data directory. Do not
store mutable databases, credentials, private signing keys, model
weights or personal data in the source repository.

## 4.17 Packaging and release output

-   `AetherOS->packaging->base->aether-base.package` --- package
    essential base OS configuration and integration.
-   `AetherOS->packaging->kernel->linux-aether.package` --- package the
    built upstream-derived Aether kernel.
-   `AetherOS->packaging->kernel->linux-aether-modules.package` ---
    package matching kernel modules.
-   `AetherOS->packaging->desktop->aether-shell.package` --- package the
    native shell and session integration.
-   `AetherOS->packaging->applications->aether-files.package` ---
    package the native file manager.
-   `AetherOS->packaging->applications->aether-settings.package` ---
    package system settings.
-   `AetherOS->packaging->ai->aether-runtime.package` --- package
    Runtime and its service/API.
-   `AetherOS->packaging->ai->aether-intentfs.package` --- package
    IntentFS and supported extractors.
-   `AetherOS->packaging->ai->aether-miso.package` --- package Miso
    agent, UI integration and policy client.
-   `AetherOS->packaging->ai->aether-capability-broker.package` ---
    package the broker and privileged helper interfaces.
-   `AetherOS->packaging->ai->aether-action-ledger.package` --- package
    action history service and migrations.
-   `AetherOS->packaging->installer->aether-installer.package` ---
    package the native installer.
-   `AetherOS->packaging->recovery->aether-recovery.package` --- package
    recovery services and UI.
-   `AetherOS->packaging->updater->aether-updater.package` --- package
    update orchestration.
-   `AetherOS->packaging->manifests->base.yaml` --- define the packages
    required for a bootable system.
-   `AetherOS->packaging->manifests->desktop.yaml` --- define the full
    native desktop package set.
-   `AetherOS->packaging->manifests->installer.yaml` --- define the
    installer image package set.
-   `AetherOS->packaging->manifests->recovery.yaml` --- define the
    recovery package set.
-   `AetherOS->release->sbom->` --- generate the release software bill
    of materials.
-   `AetherOS->release->checksums->` --- retain checksums for the exact
    ISO and associated artifacts.
-   `AetherOS->release->signatures->` --- retain public release
    signatures and verification instructions; never commit private
    signing keys.
-   `AetherOS->release->source-manifest->` --- identify source revisions
    and license information for release components.
-   `AetherOS->artifacts->AetherOS-<version>-x86_64.iso` --- final
    bootable ISO produced by the release build.
-   `AetherOS->artifacts->AetherOS-<version>-x86_64.iso.sha256` ---
    checksum file for the final ISO.
-   `AetherOS->artifacts->build-provenance.json` --- record exact
    source, toolchain, package and build inputs for the artifact.
-   `AetherOS->artifacts->release-notes.md` --- document release
    features, known hardware limits and installation instructions.

The exact package recipe format may follow the chosen base distribution.
Keep package boundaries clear; do not invent a new package format unless
the chosen base cannot meet a stated requirement. The final ISO must be
reproducible from the pinned source and build configuration, and must
include the required boot and installer artifacts.

------------------------------------------------------------------------

# 5. AI integration across the OS --- boundaries and required behavior

AI should improve discovery, explanations and user-approved automation
where it adds value, but deterministic OS behavior must remain
deterministic.

  -------------------------------------------------------------------------
  OS area                 Required Aether           Boundary
                          integration               
  ----------------------- ------------------------- -----------------------
  Boot and kernel         Explain boot/service      No LLM dependency in
                          errors after startup;     boot-critical or
                          show diagnostic facts     kernel-critical paths

  Hardware and            Explain measured          Show measured facts
  performance             CPU/RAM/storage/thermal   separately from
                          state; recommend suitable estimates
                          local model               

  Memory pressure         Pause background          Never ask the model to
                          indexing, reduce context  manage memory directly
                          or unload model under     
                          Runtime policy            

  Files and storage       IntentFS concepts/search; No silent deletion;
                          explain storage use;      normal file operations
                          propose safe cleanup      work without AI

  Networking              Explain connection state  No private data
                          and offer supported       transfer without
                          configuration steps       explicit authorization

  Package management      Explain dependencies,     Installation/update
                          release notes and install still uses the trusted
                          plans                     package manager and
                                                    confirmation

  Settings                Translate user intent     Broker enforces
                          into typed, validated     permissions; no
                          setting changes           arbitrary config
                                                    editing

  Desktop/windows         Arrange windows, launch   Native window manager
                          installed apps and        owns actual state
                          restore approved          
                          workspaces                

  Diagnostics             Summarize real logs and   Never invent logs or
                          service state, marking    claim a repair occurred
                          uncertain interpretation  without verifying it

  Accessibility           Optional plain-language   Accessible controls
                          help and voice interface  must work without AI

  Documents/code          Optional local assistance User data stays local
                          through Runtime           by default; app save
                                                    behavior remains
                                                    deterministic

  Notifications           Summarize selected actual Distinguish measured
                          events                    events from generated
                                                    interpretation

  Power/thermal           Adapt background          Respect system power
                          inference/indexing to     and thermal controls
                          real system state         

  Recovery                Explain available repair  Recovery tools use
                          actions and their effects deterministic
                                                    operations and explicit
                                                    consent
  -------------------------------------------------------------------------

------------------------------------------------------------------------

# 6. Non-negotiable user journeys

The final system must implement these complete journeys with real state,
not illustrative UI:

1.  **Boot to desktop:** firmware → bootloader → kernel → initramfs →
    root filesystem → service manager → login/session → native desktop.
2.  **Install Aether:** boot ISO → choose install → identify target disk
    → review partition/encryption plan → explicitly confirm destructive
    changes → install packages/kernel/initramfs/bootloader → create
    account → reboot into installed Aether.
3.  **First boot without AI:** configure language, keyboard, timezone,
    user/session and privacy; skip model setup; finish in a fully usable
    desktop.
4.  **First boot with AI:** profile hardware → present compatible
    recommendations and limits → obtain download consent → download →
    verify catalog and artifact integrity → configure backend → load
    model → run bounded inference verification → show actual outcome.
5.  **Search by meaning:** create or modify a supported file → watcher
    notices event → extractor reads permitted content → local model
    predicts three distinct concepts → validator checks output → record
    is stored → Files search retrieves it by filename, concept or
    supported extracted text.
6.  **Handle indexing failure:** unsupported format, permission denial,
    unavailable model or invalid output results in a clear
    pending/failed/excluded status; ordinary file access remains
    available.
7.  **Ask Miso to act:** parse request → construct plan → choose
    registered capabilities → validate inputs → check permissions/risk →
    preview and obtain confirmation when required → execute → verify
    actual state → append Action Ledger entry → show result and
    undo/recovery option where feasible.
8.  **Cancel a task:** user cancels an in-progress request →
    cancellation propagates to service/backend → no new side effects
    start → partial effects are reported accurately and recovery is
    offered where possible.
9.  **Restore a Living Workspace:** show saved context and proposed
    apps/layout → preview → user approves → restore supported state → do
    not execute shell commands or scripts.
10. **Update and recover:** verify signed metadata → show change summary
    → check compatibility and space → apply through the selected update
    mechanism → detect failure → restore known-good state or expose
    recovery instructions.
11. **Inspect an error:** display real service state and logs → redact
    secrets → explain observed facts separately from model-generated
    interpretation → offer only supported remediation.
12. **Remove a model:** stop inference safely → remove selected model
    files and registry state → release storage → leave the OS and other
    models functional.

------------------------------------------------------------------------

# 7. Release acceptance gates

The following are mandatory conditions for calling the deliverable
final. These gates are not a request to create a sample build or a
browser demo.

## Bootable OS and installation

-   The ISO is a real bootable image with a working bootloader, kernel,
    initramfs and live root filesystem.
-   The installer writes a complete system to physical storage, installs
    the boot path and creates a usable account/session.
-   Firmware support and hardware limits are documented accurately.
-   Core boot and login do not depend on an installed model or network
    access.

## Core OS and native desktop

-   Accounts, permissions, filesystems, storage mounts, networking,
    audio, display/input, service management, logs, shutdown and power
    management use real system facilities.
-   Desktop shell, windows, taskbar, launcher, notifications, focus
    mode, settings and Miso visuals run as native desktop components.
-   Every visible application/control has a real implementation or is
    visibly disabled with a specific explanation.
-   Files and Terminal operate on the actual filesystem and a real PTY;
    Writer saves actual documents; Settings changes supported live
    settings; System Monitor reads actual system state.

## Aether Runtime

-   Hardware profile is derived from real interfaces and distinguishes
    unknown values from measured values.
-   Recommendations account for RAM headroom, CPU features, supported
    acceleration, model format, task, context, disk space, backend
    compatibility and license.
-   Download is consent-based, cancellable and integrity-verified.
-   The selected model is actually loaded and its inference result is
    verified.
-   A model/backend failure cannot break the desktop or core OS.

## IntentFS

-   Supported files are indexed within user permissions and exclusions.
-   Every successful supported indexed record contains exactly three
    distinct validated local-model-predicted concepts.
-   Invalid generation is retried a bounded number of times, then shown
    as failed/pending; no hard-coded substitute concepts are presented
    as model output.
-   Search returns grounded results and explains match reasons.
-   Clearing/rebuilding the index never deletes or modifies original
    files.

## Miso, CapabilityOS and Action Ledger

-   All actions are registered, schema-validated and permission-checked.
-   AI-originated privileged operations go through the broker and
    narrowly scoped helpers.
-   Consequential actions have accurate previews and confirmation
    requirements.
-   Results are verified against real system state; history is
    persistent and secrets are redacted.
-   Cancellation, timeouts, bounded loops and supported
    undo/compensation work as described.

## Security, privacy and operations

-   The agent is unprivileged and sandboxed according to the selected
    platform.
-   Model output is never directly executed as shell code.
-   No private data is silently sent to a remote service.
-   Package/model/update artifacts are verified against trusted
    metadata.
-   Recovery, update rollback, configuration repair and IntentFS rebuild
    have real implementations.
-   Accessibility and reduced-motion preferences are applied across the
    shell and built-in apps.

## Release integrity

-   The release includes source manifests, licenses, dependency
    provenance, SBOM, checksums and release notes.
-   The ISO filename corresponds to the artifact actually generated.
-   The delivered source tree and binary artifacts agree on version and
    provenance.
-   No required component is represented by an empty file, placeholder
    implementation, fake state or future-work note.

------------------------------------------------------------------------

# 8. Prohibited shortcuts and failure conditions

The following are release-blocking defects:

-   Delivering only `aether-ui.html`, a browser window, a web server, a
    desktop theme or an application running inside another OS.
-   Delivering a folder tree, design document, static screenshots or a
    boot menu without the actual operating system behind it.
-   Creating empty source files to make the folder tree look complete.
-   Replacing real kernel source with invented files or writing a
    general-purpose kernel from scratch instead of using upstream Linux.
-   Hard-coding hardware profiles, model choices, concept tags, service
    status, progress values, app contents or action results.
-   Returning success from an operation before the owning service
    confirms the result.
-   Using fixed fake data when a real backend fails.
-   Hiding errors, silently skipping required components or treating
    unavailable features as successful.
-   Executing model-generated shell commands or allowing the agent to
    bypass the broker.
-   Requiring cloud AI or Ollama for core OS use.
-   Making model installation mandatory to complete OS installation.
-   Allowing indexing to alter file contents or cross user permissions.
-   Deleting user data without clear authorization and an accurate
    target preview.
-   Leaving essential functionality as a TODO, FIXME, stub, mock, demo
    or "future improvement."
-   Claiming the operating system is finished before the ISO, installer,
    desktop, system services and required AI components are integrated
    into the release.

If a third-party component, driver, model format or hardware feature is
unavailable, document the exact limitation, provide a safe fallback
where specified and make the state visible. Do not disguise a limitation
with fabricated behavior.

------------------------------------------------------------------------

# 9. Final implementation and handover requirements

The implementation is complete only when the repository contains the
fully integrated source/configuration/package tree, the bootable ISO and
its required release metadata, plus the user documentation needed to
install, operate, update and recover the system.

The handover must include:

-   Complete source tree following the approved Aether structure.
-   Pinned upstream kernel source reference, kernel configuration, patch
    rationale and build provenance.
-   Native desktop and all required built-in applications.
-   Aether Runtime, backend interface, model catalog format, model
    manager, resource governor and first-boot setup.
-   IntentFS extractors, local concept generation/validation, metadata
    store, search service and Files integration.
-   Miso agent, CapabilityOS registry, broker, policy engine, Action
    Ledger and Living Workspaces.
-   Security/privacy policy, permissions, accessibility and localization
    resources.
-   Installer, boot configuration, initramfs, package/update handling
    and recovery tools.
-   Actual bootable ISO, checksum, release manifest, software bill of
    materials, source/license inventory and release notes.
-   `README.md` and user guides explaining supported hardware,
    installation, first boot, local model setup, privacy,
    troubleshooting and recovery.
-   No embedded private signing keys, user secrets or unlicensed model
    artifacts.

## Final directive

Implement Aether as the complete final operating system described by the
approved folder structure and project idea document. Preserve the
product scope. Do not replace the OS with a browser application, a
prototype, a partial implementation or an add-on. Do not hard-code
behavior, fake service responses, leave required features for later, or
deviate because the work is large. Implement every required subsystem,
connect the components through real interfaces, handle failure safely,
and deliver the actual bootable ISO with the source and release
materials needed to operate and maintain it.

This document defines the required implementation target; it is not a
claim that the OS has already been built.
