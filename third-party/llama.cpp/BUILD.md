# Building llama.cpp for Aether
Build llama-server only (no models vendored):

    cmake -B build -DGGML_NATIVE=ON -DLLAMA_CURL=OFF
    cmake --build build --target llama-server -j$(nproc)

Install binary to /usr/lib/aether/backends/llama-server (aether-ai optional
dependency). GPU builds: add -DGGML_CUDA=ON (or VULKAN) when the target has
accelerator support; the Runtime probes GPU capability and offloads only when
both the device AND build support it.
