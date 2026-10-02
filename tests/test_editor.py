from kmxradar.editor import validate_editorial


def test_rejects_invented_number():
    payload = {
        "headline": "Un evento importante deja 99 afectados",
        "summary": "La información continúa en desarrollo.",
        "known": ["Hay confirmación oficial."],
        "unknown": [],
        "source_domains": ["example.org"],
    }
    evidence = "La autoridad informó que el evento ocurrió esta mañana."
    assert not validate_editorial(payload, evidence)


def test_accepts_supported_number():
    payload = {
        "headline": "Un evento deja 12 afectados según la autoridad",
        "summary": "La información continúa en desarrollo.",
        "known": ["La cifra comunicada es 12."],
        "unknown": [],
        "source_domains": ["example.org"],
    }
    evidence = "La autoridad informó que 12 personas resultaron afectadas."
    assert validate_editorial(payload, evidence)
