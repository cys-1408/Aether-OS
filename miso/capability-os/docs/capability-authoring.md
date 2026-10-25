# Capability Authoring
1. Add an entry to the right group catalog (miso/capability-os/schemas/<group>.capabilities.json)
   with all required fields (id, version, provider, risk_class, permission, timeout_s,
   idempotent, side_effects, confirmation, input/output schemas, undo).
2. Implement the executor in miso/capabilities/<group>/<id>.py — argv-list subprocesses
   only, no shell interpolation, path scope checks via aether_core.filesops.
3. Register the dispatch route in miso/broker/execution_dispatcher.py.
4. Verify with `python3 -c "from miso.capability_os.registry.capability_registry import load_registry"`.

Rules: destructive capabilities need confirmation=always; agent-requested destructive
ops that format/delete/alter security are DENIED by policy outright; every capability
returns schema-valid results with truthful errors.
