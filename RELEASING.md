# Releasing the Lexibank clld app

1. Create a SQLite database loaded with the lexibank-analysed wordlist dataset:
   ```shell
   rm -f ../lexibank.sqlite
   cldf createdb ../lexibank-analysed/cldf/wordlist-metadata.json ../lexibank.sqlite
   ```
2. Run
   ```shell
   clld initdb development.ini --cldf ../lexibank-analysed/cldf/wordlist-metadata.json
   ```
