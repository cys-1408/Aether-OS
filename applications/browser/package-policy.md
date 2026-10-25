# Browser Package Policy

Aether does NOT ship a browser in the base image (build/manifests/excluded-packages.yaml).
Policy:
1. Users install a maintained browser as a normal package via Software Center
   (e.g. firefox, chromium, falkon from the distro repos).
2. The browser is an ordinary application under the session — it is never the
   host of the desktop shell, and the shell never renders web content as OS UI.
3. Optional local summarization of web pages, if ever added, goes through the
   Aether Runtime with explicit per-use consent (no silent data egress).
4. `default-browser.desktop` below registers the installed browser with xdg-settings
   once the user installs one.
