# Desktop Shell (native)

`aether-shell` is a GTK3 (PyGObject) process running in a sway session.
Panels use gtk-layer-shell where available (guarded import, graceful
fallback). Window management goes through sway IPC (aether_core.swayipc).
The shell hosts the Shell.* JSON-RPC server consumed by the broker for
app/window capabilities. Design tokens in theme/*.yaml reproduce the
approved reference exactly (CONVENTIONS.md §9).
