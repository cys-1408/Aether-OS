# Third-Party Pins
All third-party sources are fetched at BUILD time with digest verification.
Nothing vendored is committed. pins.yaml records version + source + license;
build/scripts/10-fetch-sources.sh verifies digests before use.
