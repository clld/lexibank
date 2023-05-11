import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/contributions'),
        ('get_html', '/parameters'),
        ('get_html', '/parameters/1007#2/14.4/145.3'),
        ('get_html', '/languages'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
