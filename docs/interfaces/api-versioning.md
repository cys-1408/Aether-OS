# API Versioning
Every socket answers a `X.info` method ({service, api_version}). Version policy: additive params/methods = minor; breaking change = major bump with a parallel socket name during transition (e.g. runtime-v2.sock). aether_core.ipc.call enforces expected version ranges. API_VERSIONS is pinned in aether_core/version.py and mirrored in docs.
