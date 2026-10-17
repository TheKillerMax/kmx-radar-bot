import sys
import kmxradar.cli as cli


def test_check_instagram_uses_verified_account_without_printing_secret(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["kmx-radar", "check-instagram"])
    monkeypatch.setattr(cli, "get_verified_account", lambda: (
        "do-not-print-this-secret", {"user_id": "1234", "username": "kmxradar", "account_type": "BUSINESS"}
    ))
    assert cli.main() == 0
    output = capsys.readouterr().out
    assert "kmxradar" in output
    assert "do-not-print-this-secret" not in output
