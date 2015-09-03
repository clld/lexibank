from setuptools import setup, find_packages


requires = [
    'clld>=1.5.1',
    'clldmpg>=1.0.0',
    'clld-glottologfamily-plugin',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'mock',
]


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
    install_requires=requires,
    tests_require=tests_require,
    test_suite="lexibank",
    entry_points="""\
[paste.app_factory]
main = lexibank:main
""")
