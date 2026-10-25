# Session Boundaries
System services run as dedicated users and never read user homes. User-session
services (shell, agent, trash, clipboard, reminders) run under the logged-in
user with sockets under /run/user/$UID/aether/. The broker matches agent
requester uid against SO_PEERCRED uid; mismatch = denied. Other users' files
are outside the broker's path scope by policy (capability-policy.yaml).
