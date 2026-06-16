from setuptools import setup, find_packages


setup(
    name='lexibank',
    version='0.0',
    description='lexibank',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clldutils>=4',
        'pyclts>=4.0.2',
        'clld>=11.5',
        'clldmpg>=4.2',
        'clld-glottologfamily-plugin>=2.0.1',
        'clld-ipachart-plugin>=1.0',
        'pycldf>=2',
        'sqlalchemy',
        'waitress',
        'matplotlib',
    ],
    extras_require={
        'dev': [
            'flake8',
            'tox'
        ],
        'test': [
            'psycopg2',
            'pytest>=3.1',
            'pytest-clld',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    test_suite="lexibank",
    entry_points="""\
[paste.app_factory]
main = lexibank:main
""")
