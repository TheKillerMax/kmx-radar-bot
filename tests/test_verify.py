from kmxradar.models import Article, Cluster
from kmxradar.verify import verify_cluster


def test_primary_plus_independent_sources_can_pass():
    articles = [
        Article(title="Evento A", url="https://usgs.gov/a", domain="usgs.gov", primary_hint=True),
        Article(title="Evento A", url="https://reuters.com/a", domain="reuters.com"),
        Article(title="Evento A", url="https://bbc.com/a", domain="bbc.com"),
        Article(title="Evento A", url="https://apnews.com/a", domain="apnews.com"),
        Article(title="Evento A", url="https://elpais.com/a", domain="elpais.com"),
    ]
    cluster = Cluster(key="x", category="MUNDO", risk="medium", articles=articles)
    verified = verify_cluster(cluster)
    assert verified.primary_source_present
    assert verified.verification_score >= 0.77
    assert verified.publishable


def test_single_source_does_not_publish():
    cluster = Cluster(
        key="x",
        category="MUNDO",
        risk="low",
        articles=[Article(title="Evento A", url="https://random.example/a", domain="random.example")],
    )
    verified = verify_cluster(cluster)
    assert not verified.publishable
