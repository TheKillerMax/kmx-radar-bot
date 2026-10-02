from kmxradar.graphics import render_news_card
from kmxradar.models import Article, Cluster


def test_render_card(tmp_path, monkeypatch):
    import kmxradar.graphics as graphics
    monkeypatch.setattr(graphics, "DOCS_DIR", tmp_path)
    cluster = Cluster(
        key="demo",
        category="CIENCIA",
        risk="low",
        articles=[Article(title="Hallazgo científico de prueba", url="https://example.org/x", domain="example.org")],
        independent_domains=["example.org", "example.net", "example.com"],
        status="CORROBORADO",
    )
    path = render_news_card(cluster, {
        "headline": "Hallazgo científico de prueba para KMX RADAR",
        "summary": "Una tarjeta automática muestra cómo se presentará la información contrastada.",
        "known": [],
        "unknown": [],
        "source_domains": ["example.org", "example.net", "example.com"],
    })
    assert path.exists()
    assert path.suffix == ".jpg"
