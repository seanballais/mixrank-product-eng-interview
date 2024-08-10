import pytest

from compmatrix import routing


@pytest.fixture
def test_data_routes():
    def test_view_index():
        return ''

    def test_view_a():
        return 'a'

    def test_view_ab():
        return 'ab'

    routes = [
        routing.Route('/', test_view_index),
        routing.Route('/a', test_view_a),
        routing.Route('/a/b', test_view_ab),
    ]
    yield routes
