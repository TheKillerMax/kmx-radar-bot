from kmxradar.cluster import cluster_articles
from kmxradar.models import Article


def test_similar_headlines_cluster():
    rows = [
        Article(title="Fuerte terremoto sacude una región del Pacífico", url="https://a.example/1", domain="a.example", category="MUNDO"),
        Article(title="Un fuerte terremoto sacude región del Pacífico", url="https://b.example/2", domain="b.example", category="MUNDO"),
        Article(title="Nueva misión espacial despega con éxito", url="https://c.example/3", domain="c.example", category="CIENCIA"),
    ]
    clusters = cluster_articles(rows)
    assert len(clusters) == 2
    assert max(len(c.articles) for c in clusters) == 2
