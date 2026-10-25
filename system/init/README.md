# Init and Service Manager Policy
systemd is the init system (ADR-0003). Units ship under system/services,
targets under system/targets, timers under system/timers. dependency-graph.yaml
is the human-readable source of truth mirrored in unit After=/Requires=;
shutdown-order.yaml lists persistence-sensitive ordering.
