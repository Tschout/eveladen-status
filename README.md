# eveladen-status

Vrij/bezet per laadlocatie in Nederland, elke tien minuten ververst uit de open data van het [NDW](https://opendata.ndw.nu).
Wordt gebruikt door [eveladen.nl](https://eveladen.nl).

Per plaats één bestand: `https://tschout.github.io/eveladen-status/<plaats>.json`

```json
{"t": 1795594853, "s": {"<locatie-id>": [2, 6, 0]}}
```

`t` is het tijdstip van ophalen (seconden sinds 1970), de drie getallen zijn laadpunten vrij, bezet en buiten gebruik.
