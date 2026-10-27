"""Esempio per il testo: tre decennali con lo stesso rendimento (BTP guida al 30/9/2026) e cedole diverse.
Mostra che il cuscinetto dipende dalla durata del titolo, non solo dal rendimento.

Uso:  python codice/esempio_fuori_pari.py
"""
from scipy.optimize import brentq

from obbligazioni import durata_modificata, prezzo

Y0 = 4.58875  # BTP 10 anni guida, 30/9/2026 (Banca d'Italia, BMK0200)

for cedola in (1.0, Y0, 7.0):
    p0 = prezzo(cedola, Y0, 10, 2)
    rend = lambda y1: (cedola + prezzo(cedola, y1, 9, 2) - p0) / p0 * 100
    soglia = brentq(rend, -5, 30)
    d = durata_modificata(cedola, Y0, 9, 2)
    print(f"cedola {cedola:5.2f}%  prezzo {p0:6.2f}  durata fra un anno {d:4.2f}  "
          f"soglia {soglia:4.2f}%  cuscinetto {100 * (soglia - Y0):3.0f} pb  formula Nangle {Y0 + Y0 / d:4.2f}%")
