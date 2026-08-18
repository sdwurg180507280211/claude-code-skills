# Upstream

This directory is a vendored, intentionally unmodified copy of the upstream `content-research-writer` Skill so it can be installed from this repository's marketplace bundle.

- Upstream repository: `CommandCodeAI/agent-skills`
- Upstream path: `skills/content-research-writer/SKILL.md`
- Pinned audited commit: `f490dd9016f2729311e90f317dcb6c98be1a1500`
- Upstream file blob at time of vendoring: `d9e6f12fe51f61225fde6844dba8c3edf530703f`
- Vendored file blob: `910a914144e2def10038dd9472e72a4a9d6c9a9c`
- License: MIT; see `LICENSE`
- Local integrity lock: `UPSTREAM.lock.json`

## Policy

- Keep the substantive `SKILL.md` content aligned with the pinned upstream; do not add local writing or medical behavior to it.
- The current vendored blob differs from the source blob only because the local copy has no terminal newline. The text content is otherwise aligned with the pinned upstream.
- `UPSTREAM.lock.json` records both the source blob and the expected local vendored blob. Repository validation fails if the local vendored file drifts without an explicit lock update.
- Medical domain context and medical fact constraints remain in `wechat-medical-writer`.
- When updating upstream, review the upstream diff first, replace the vendored file, then update the pinned commit, source blob, vendored blob and lock together.
