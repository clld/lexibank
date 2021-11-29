import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/contributions'),
        ('get_html', '/contributions/pollex'),
        ('get_html', '/parameters'),
        ('get_html', '/parameters/1007#2/14.4/145.3'),
        ('get_html', '/languages'),
        ('get_html', '/languages/agua1252'),
        ('get_html', '/sources/numerals-2'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
