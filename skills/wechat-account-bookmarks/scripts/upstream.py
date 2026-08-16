#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ARCHIVE_REPO_URL = "https://github.com/freestylefly/wechat-article-archive-skill.git"
ARCHIVE_COMMIT = "4820880eb51de1f05683a1511657db3a8cea59d0"
EXTRACTOR_REPO_URL = "https://github.com/freestylefly/wechat-article-extractor-skill.git"
EXTRACTOR_COMMIT = "d8f74b8946065e64537f1ad39f962dbed86da3c7"


@dataclass(frozen=True)
class UpstreamPaths:
    archive_repo: Path
    extractor_repo: Path

    @property
    def discover_script(self) -> Path:
        return self.archive_repo / "scripts" / "discover_account_articles.py"

    @property
    def extractor_script(self) -> Path:
        return self.extractor_repo / "scripts" / "extract.js"


def _run(
    cmd: list[str],
    cwd: Path | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def _require_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"缺少命令：{name}")
    return path


def _ensure_repo(path: Path, repo_url: str, commit: str) -> None:
    git = _require_command("git")
    just_cloned = False
    if not (path / ".git").is_dir():
        path.parent.mkdir(parents=True, exist_ok=True)
        _run([git, "clone", "--filter=blob:none", "--no-checkout", repo_url, str(path)])
        just_cloned = True

    try:
        head = _run([git, "rev-parse", "HEAD"], cwd=path).stdout.strip()
    except subprocess.CalledProcessError:
        head = ""

    if just_cloned or head != commit:
        _run([git, "fetch", "origin", commit, "--depth", "1"], cwd=path)

    # --no-checkout leaves a freshly cloned worktree empty even when HEAD already
    # equals the pinned commit. Always checkout the pinned commit so required
    # scripts/package files are materialized on disk.
    _run([git, "checkout", "--detach", commit], cwd=path)


def _ensure_extractor_dependencies(repo: Path) -> None:
    _require_command("node")
    npm = _require_command("npm")
    if (repo / "node_modules").is_dir():
        return
    _run([npm, "ci", "--omit=dev"], cwd=repo, timeout=600)


def ensure_upstreams(
    cache_dir: Path,
    archive_repo: Path | None = None,
    extractor_repo: Path | None = None,
    bootstrap: bool = True,
) -> UpstreamPaths:
    cache_dir = cache_dir.expanduser().resolve()
    archive = (archive_repo or (cache_dir / "wechat-article-archive-skill")).expanduser().resolve()
    extractor = (extractor_repo or (cache_dir / "wechat-article-extractor-skill")).expanduser().resolve()

    if bootstrap:
        if archive_repo is None:
            _ensure_repo(archive, ARCHIVE_REPO_URL, ARCHIVE_COMMIT)
        elif not archive.is_dir():
            raise RuntimeError(f"找不到 archive 上游仓库：{archive}")

        if extractor_repo is None:
            _ensure_repo(extractor, EXTRACTOR_REPO_URL, EXTRACTOR_COMMIT)
        elif not extractor.is_dir():
            raise RuntimeError(f"找不到 extractor 上游仓库：{extractor}")
        _ensure_extractor_dependencies(extractor)
    else:
        if not archive.is_dir():
            raise RuntimeError(f"找不到 archive 上游仓库：{archive}")
        if not extractor.is_dir():
            raise RuntimeError(f"找不到 extractor 上游仓库：{extractor}")
        _require_command("node")

    paths = UpstreamPaths(archive_repo=archive, extractor_repo=extractor)
    if not paths.discover_script.is_file():
        raise RuntimeError(f"缺少上游脚本：{paths.discover_script}")
    if not paths.extractor_script.is_file():
        raise RuntimeError(f"缺少上游脚本：{paths.extractor_script}")
    return paths
