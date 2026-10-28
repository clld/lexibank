# Releasing the Lexibank clld app

```shell
git clone --branch v2.2 --depth 1 https://github.com/lexibank/lexibank-analysed
git clone --branch v2.3.1 --depth 1 https://github.com/cldf-clts/clts-data
git clone --branch v1.0 --depth 1 https://github.com/clics/clics4
git clone https://github.com/clld/lexibank
cd lexibank
pip install -e .[test]
```


1. Create a SQLite database loaded with the lexibank-analysed wordlist dataset:
   ```shell
   cd ../lexibank-analysed
   rm -f lexibank.sqlite
   cldf createdb cldf/wordlist-metadata.json lexibank.sqlite
   ```
2. Run
   ```shell
   clld initdb development.ini --cldf ../lexibank-analysed/cldf/wordlist-metadata.json
   ```

