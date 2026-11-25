"""Maakt per plaats een klein bestand met hoeveel laadpunten vrij of bezet zijn.

Bron: open data van het NDW (https://opendata.ndw.nu), dat elke minuut wordt ververst.
Gebruik: python3 status.py <uitvoermap>
Uitvoer: <uitvoermap>/<plaats>.json = {"t": tijdstip, "s": {locatie-id: [vrij, bezet, buiten gebruik]}}
"""
import gzip
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from collections import defaultdict

BRON = "https://opendata.ndw.nu/charging_point_locations_ocpi.json.gz"
ZICHTBAAR = {"AVAILABLE", "CHARGING", "BLOCKED", "RESERVED", "UNKNOWN", "OUTOFORDER", "INOPERATIVE"}
ALIAS = {"s-gravenhage": "den-haag", "the-hague": "den-haag", "den-bosch": "s-hertogenbosch"}


def slug(tekst):
    t = unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return ALIAS.get(t, t)


def main(uit):
    os.makedirs(uit, exist_ok=True)
    pad = os.path.join(uit, "_bron.json.gz")
    urllib.request.urlretrieve(BRON, pad)
    tijd = int(time.time())
    with gzip.open(pad) as f:
        locaties = json.load(f)
    os.remove(pad)
    plaatsen = defaultdict(dict)
    for l in locaties:
        if l.get("publish") is False or (l.get("country") or "NLD") not in ("NLD", "NL"):
            continue
        co = l.get("coordinates") or {}
        try:
            lat, lng = float(co["latitude"]), float(co["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
        s = slug((l.get("city") or "").strip())
        if not s or not (50.7 < lat < 53.6 and 3.3 < lng < 7.3):
            continue
        stand = [0, 0, 0]  # vrij, bezet, buiten gebruik; onbekend telt niet mee
        for ev in l.get("evses") or []:
            st = ev.get("status")
            if st not in ZICHTBAAR or st == "UNKNOWN":
                continue
            stand[0 if st == "AVAILABLE" else 2 if st in ("OUTOFORDER", "INOPERATIVE") else 1] += 1
        if sum(stand):
            plaatsen[s][l["id"]] = stand
    for s, stand in plaatsen.items():
        with open(os.path.join(uit, s + ".json"), "w") as f:
            json.dump({"t": tijd, "s": stand}, f, separators=(",", ":"))
    with open(os.path.join(uit, "index.html"), "w") as f:
        f.write('<!doctype html><meta charset="utf-8"><title>eveladen status</title><p>Vrij/bezet per laadlocatie voor <a href="https://eveladen.nl">eveladen.nl</a>, uit open data van het NDW.</p>')
    print(len(plaatsen), "plaatsen,", sum(len(v) for v in plaatsen.values()), "locaties met status")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "uit")
