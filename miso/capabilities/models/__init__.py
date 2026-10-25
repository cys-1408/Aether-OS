"""Model capabilities: thin, JSON-RPC callers of the Aether Runtime.

Executors never shell out and never fabricate model data; everything comes
from `/run/aether/runtime.sock` and failures are reported verbatim.
"""
