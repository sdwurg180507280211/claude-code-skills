# Upstream

This directory is a vendored, intentionally unmodified copy of the upstream `content-research-writer` Skill so it can be installed from this repository's marketplace bundle.

- Upstream repository: `CommandCodeAI/agent-skills`
- Upstream path: `skills/content-research-writer/SKILL.md`
- Pinned audited commit: `f490dd9016f2729311e90f317dcb6c98be1a1500`
- Upstream file blob at time of vendoring: `d9e6f12fe51f61225fde6844dba8c3edf530703f`
- License: MIT; see `LICENSE`

## Policy

- Keep `SKILL.md` byte-for-byte aligned with the pinned upstream when refreshing it.
- Do not add medical-specific behavior to this vendored Skill.
- Medical domain context and medical fact constraints remain in `wechat-medical-writer`.
- When updating, review the upstream diff first, then replace the vendored file and update the pinned commit/blob above.
