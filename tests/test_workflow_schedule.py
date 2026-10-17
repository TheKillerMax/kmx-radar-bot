from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _workflow(name: str) -> dict:
    text = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
    # BaseLoader treats the GitHub Actions key "on" as a string (not YAML 1.1 boolean).
    return yaml.load(text, Loader=yaml.BaseLoader)


def test_collector_uses_local_chilean_timezone_through_dst():
    cfg = _workflow("radar.yml")
    schedule = cfg["on"]["schedule"]
    assert schedule == [
        {"cron": "5 0,6,12,18 * * *", "timezone": "America/Santiago"}
    ]


def test_all_repo_writers_share_same_mutex():
    for name in ("radar.yml", "prepare-visuals.yml", "publish-approved.yml", "refresh-token.yml"):
        cfg = _workflow(name)
        assert cfg["concurrency"]["group"] == "kmx-radar-main-writer"
        assert cfg["concurrency"]["cancel-in-progress"] == "false"


def test_writing_workflows_call_bounded_push_helper():
    for name in ("radar.yml", "prepare-visuals.yml", "publish-approved.yml", "refresh-token.yml"):
        text = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        assert "bash .github/scripts/push-main-safely.sh" in text
        assert "git push --force" not in text
