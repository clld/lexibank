# Releasing the Lexibank clld app

```shell
git clone --branch v2.2.5 --depth 1 https://github.com/lexibank/lexibank-analysed
git clone --branch v2.3.1 --depth 1 https://github.com/cldf-clts/clts clts-data
git clone --branch v1.0 --depth 1 https://github.com/clics/clics4
git clone https://github.com/clld/lexibank
cd lexibank
pip install -e .[test]
```


Create a SQLite database loaded with the lexibank-analysed wordlist dataset.
```shell
cd ../lexibank-analysed
rm -f lexibank.sqlite
cldf createdb cldf/wordlist-metadata.json lexibank.sqlite
cd ../lexibank
```

Run
```shell
clld initdb development.ini --cldf ../lexibank-analysed/cldf/wordlist-metadata.json --glottolog ../../glottolog/glottolog
```
Note that this requires the `gh` tool to download releases of the individual
datasets from GitHub.

```shell
pytest
```

Store the tested requirements:
```shell
pip freeze > requirements.txt
```

Store a db dump:
```shell
pg_dump -xO lexibank > lexibank.sql
zip lexibank.sql.zip lexibank.sql
rm lexibank.sql
```

