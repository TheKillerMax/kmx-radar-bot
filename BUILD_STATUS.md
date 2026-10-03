# Build status

- Instagram connection workflow: successful.
- Architecture migrated to **ChatGPT as editor**; no local LLM runtime remains.
- The collector creates ZIP evidence packages as GitHub Actions artifacts.
- Automated Instagram publication is disabled unless `PUBLISH_ENABLED=true`.
- Approved packages can contain 1–10 images and are published only when a final `.ready` marker exists.
- Token renewal remains automated and encrypted.
