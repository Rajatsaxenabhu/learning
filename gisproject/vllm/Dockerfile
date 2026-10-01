FROM vllm/vllm-openai:latest

RUN pip install --no-cache-dir vllm-gguf-plugin

# vllm-gguf-plugin 0.0.5 doesn't normalize the "qwen3_5" HF model_type to the
# "qwen35" architecture name used by the gguf package's MODEL_ARCH_NAMES,
# so GGUF loading fails with "Unknown gguf model_type: qwen3_5" even though
# both vLLM and the gguf format support the architecture. Patch the same
# underscore-stripping normalization the plugin already applies to
# qwen2_moe/qwen3_moe onto qwen3_5/qwen3_5_moe.
RUN python3 - <<'PYEOF'
path = "/usr/local/lib/python3.12/dist-packages/vllm_gguf_plugin/weights_adapter/default.py"
with open(path) as f:
    content = f.read()

anchor = '        if model_type == "olmoe":'
patch = (
    '        if model_type in ("qwen3_5", "qwen3_5_moe"):\n'
    '            model_type = model_type.replace("_", "")\n'
    + anchor
)

if anchor not in content:
    raise SystemExit("qwen3_5 patch failed: anchor line not found in default.py")
if "qwen3_5" in content.split(anchor)[0]:
    raise SystemExit("qwen3_5 patch failed: patch already present or file changed unexpectedly")

content = content.replace(anchor, patch, 1)
with open(path, "w") as f:
    f.write(content)
print("Patched vllm_gguf_plugin: qwen3_5 -> qwen35 model_type normalization")
PYEOF